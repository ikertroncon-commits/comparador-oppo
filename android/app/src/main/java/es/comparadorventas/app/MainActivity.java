package es.comparadorventas.app;

import android.Manifest;
import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.provider.Settings;
import android.util.Base64;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * App nativa del Comparador OPPO: muestra la web comparadorventas.es dentro de la app
 * (así todo lo que se cambia en la web llega solo) y añade lo nativo: widgets,
 * identificador fijo del móvil, cámara, archivos y botón atrás sin cerrar la app.
 */
public class MainActivity extends Activity {

    static final String BASE = "https://comparadorventas.es/";
    private static final int REQ_FILE = 10;
    private static final int REQ_CAM = 11;

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private PermissionRequest pendingPermission;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.parseColor("#14141F"));

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#14141F"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setUserAgentString(s.getUserAgentString() + " ComparadorApp/" + versionName());
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true);

        web.addJavascriptInterface(new Puente(), "AndroidApp");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                String host = u.getHost();
                if (host != null && (host.equals("comparadorventas.es") || host.endsWith(".comparadorventas.es"))) {
                    return false; // se queda dentro de la app
                }
                // Enlaces externos (GSMArena, Kimovil…) se abren en el navegador
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) { }
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> {
                    boolean wantsCamera = false;
                    for (String r : request.getResources()) {
                        if (PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(r)) wantsCamera = true;
                    }
                    if (!wantsCamera) { request.deny(); return; }
                    if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                        request.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
                    } else {
                        pendingPermission = request;
                        requestPermissions(new String[]{Manifest.permission.CAMERA}, REQ_CAM);
                    }
                });
            }

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                try {
                    startActivityForResult(params.createIntent(), REQ_FILE);
                } catch (Exception e) {
                    fileCallback = null;
                    return false;
                }
                return true;
            }
        });

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(urlFor(getIntent()));
        }
    }

    private String versionName() {
        try { return getPackageManager().getPackageInfo(getPackageName(), 0).versionName; }
        catch (Exception e) { return "2"; }
    }

    /** Dirección inicial: la web, o una pantalla concreta si se abre desde el widget. */
    private String urlFor(Intent intent) {
        Uri d = intent != null ? intent.getData() : null;
        if (d != null && "comparador".equals(d.getScheme())) {
            Uri.Builder b = Uri.parse(BASE).buildUpon();
            String ir = d.getHost();
            String marca = d.getQueryParameter("marca");
            if (ir != null && !ir.equals("marca")) b.appendQueryParameter("ir", ir);
            if (marca != null) b.appendQueryParameter("marca", marca);
            return b.build().toString();
        }
        return BASE;
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        Uri d = intent.getData();
        if (d != null && "comparador".equals(d.getScheme()) && web != null) {
            String ir = d.getHost();
            String marca = d.getQueryParameter("marca");
            String js = "window.appIr ? window.appIr(" + JSONObject.quote(ir == null ? "" : ir) + ","
                    + (marca == null ? "null" : JSONObject.quote(marca)) + ") : location.href=" + JSONObject.quote(urlFor(intent));
            web.evaluateJavascript(js, null);
        }
    }

    /** Botón atrás: vuelve a la pantalla anterior de la app. En el menú principal no hace nada (no se cierra). */
    @Override
    public void onBackPressed() {
        if (web == null) return;
        web.evaluateJavascript("window.appBack ? window.appBack() : 'menu'", null);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQ_CAM && pendingPermission != null) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                pendingPermission.grant(new String[]{PermissionRequest.RESOURCE_VIDEO_CAPTURE});
            } else {
                pendingPermission.deny();
            }
            pendingPermission = null;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_FILE && fileCallback != null) {
            fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            fileCallback = null;
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        if (web != null) web.saveState(outState);
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (web != null) web.onPause();
        CookieManager.getInstance().flush();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
    }

    /** Funciones que la web puede usar a través de window.AndroidApp */
    private class Puente {

        /** Identificador fijo de este móvil para esta app (no cambia al reinstalar). */
        @JavascriptInterface
        public String deviceId() {
            String id = Settings.Secure.getString(getContentResolver(), Settings.Secure.ANDROID_ID);
            return id == null ? "" : id;
        }

        /** Modelo del móvil, p. ej. SM-A556B */
        @JavascriptInterface
        public String model() {
            return Build.MODEL;
        }

        /** Datos para los widgets: {"modelos": 55} y/o {"tema": "light"|"dark"} */
        @JavascriptInterface
        public void setWidgetData(String json) {
            try {
                JSONObject o = new JSONObject(json);
                SharedPreferences.Editor e = getSharedPreferences(Widgets.PREFS, MODE_PRIVATE).edit();
                if (o.has("modelos")) e.putInt("modelos", o.getInt("modelos"));
                if (o.has("tema")) e.putString("tema", o.getString("tema"));
                e.apply();
                Widgets.updateAll(MainActivity.this);
            } catch (Exception ignored) { }
        }

        /** Guarda un archivo (copias de seguridad) en Descargas. */
        @JavascriptInterface
        public void saveFile(String name, String base64, String mime) {
            try {
                byte[] bytes = Base64.decode(base64, Base64.DEFAULT);
                String where;
                if (Build.VERSION.SDK_INT >= 29) {
                    ContentValues v = new ContentValues();
                    v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
                    v.put(MediaStore.MediaColumns.MIME_TYPE, mime);
                    v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS);
                    ContentResolver r = getContentResolver();
                    Uri u = r.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
                    try (OutputStream os = r.openOutputStream(u)) { os.write(bytes); }
                    where = "Descargas";
                } else {
                    File dir = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
                    File f = new File(dir, name);
                    try (FileOutputStream os = new FileOutputStream(f)) { os.write(bytes); }
                    where = f.getParent();
                }
                final String msg = "Copia guardada en " + where;
                runOnUiThread(() -> Toast.makeText(MainActivity.this, msg, Toast.LENGTH_LONG).show());
            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "No se pudo guardar la copia", Toast.LENGTH_LONG).show());
            }
        }
    }
}
