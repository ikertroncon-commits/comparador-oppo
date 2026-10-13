package es.comparadorventas.app;

import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;

/** Widget grande: Escanear, Comparar y botones de cada marca. */
public class WidgetGrande extends AppWidgetProvider {
    @Override
    public void onUpdate(Context ctx, AppWidgetManager manager, int[] ids) {
        for (int id : ids) manager.updateAppWidget(id, Widgets.grande(ctx));
    }
}
