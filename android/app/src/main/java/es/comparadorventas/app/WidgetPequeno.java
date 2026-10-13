package es.comparadorventas.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;

/** Widget pequeño: un botón para abrir el escáner. */
public class WidgetPequeno extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager manager, int[] ids) {
        for (int id : ids) manager.updateAppWidget(id, Widgets.pequeno(ctx));
    }
}
