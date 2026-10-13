package es.comparadorventas.app;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.widget.RemoteViews;

/** Construye los widgets (grande y pequeño) en modo claro u oscuro, igual que la app. */
final class Widgets {

    static final String PREFS = "widget";
    private static final String[] MARCAS = {"Xiaomi", "Samsung", "Vivo", "Honor", "Motorola", "Google"};
    private static final int[] IDS_MARCA = {R.id.w_m1, R.id.w_m2, R.id.w_m3, R.id.w_m4, R.id.w_m5, R.id.w_m6};

    private Widgets() { }

    static RemoteViews grande(Context ctx) {
        SharedPreferences p = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        boolean claro = "light".equals(p.getString("tema", "dark"));
        RemoteViews rv = new RemoteViews(ctx.getPackageName(), claro ? R.layout.widget_grande_claro : R.layout.widget_grande);
        int modelos = p.getInt("modelos", -1);
        rv.setTextViewText(R.id.w_count, modelos >= 0 ? modelos + " modelos" : "");
        rv.setOnClickPendingIntent(R.id.w_head, abrir(ctx, "comparar", null, 1));
        rv.setOnClickPendingIntent(R.id.w_escanear, abrir(ctx, "escanear", null, 2));
        rv.setOnClickPendingIntent(R.id.w_comparar, abrir(ctx, "comparar", null, 3));
        for (int i = 0; i < MARCAS.length; i++) {
            rv.setOnClickPendingIntent(IDS_MARCA[i], abrir(ctx, "marca", MARCAS[i], 10 + i));
        }
        return rv;
    }

    static RemoteViews pequeno(Context ctx) {
        SharedPreferences p = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        boolean claro = "light".equals(p.getString("tema", "dark"));
        RemoteViews rv = new RemoteViews(ctx.getPackageName(), claro ? R.layout.widget_pequeno_claro : R.layout.widget_pequeno);
        rv.setOnClickPendingIntent(R.id.w_escanear, abrir(ctx, "escanear", null, 20));
        return rv;
    }

    /** Abre la app en una pantalla concreta: comparador://escanear, comparador://marca?marca=Xiaomi… */
    private static PendingIntent abrir(Context ctx, String ir, String marca, int code) {
        String uri = "comparador://" + ir + (marca != null ? "?marca=" + Uri.encode(marca) : "");
        Intent i = new Intent(ctx, MainActivity.class);
        i.setAction(Intent.ACTION_VIEW);
        i.setData(Uri.parse(uri));
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        return PendingIntent.getActivity(ctx, code, i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    /** Vuelve a pintar todos los widgets (al cambiar el tema o el número de modelos). */
    static void updateAll(Context ctx) {
        AppWidgetManager m = AppWidgetManager.getInstance(ctx);
        int[] g = m.getAppWidgetIds(new ComponentName(ctx, WidgetGrande.class));
        for (int id : g) m.updateAppWidget(id, grande(ctx));
        int[] s = m.getAppWidgetIds(new ComponentName(ctx, WidgetPequeno.class));
        for (int id : s) m.updateAppWidget(id, pequeno(ctx));
    }
}
