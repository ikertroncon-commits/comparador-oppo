# App nativa Comparador OPPO

App Android que muestra comparadorventas.es y añade widgets (grande y pequeño).

- Cada cambio en esta carpeta hace que GitHub genere una APK nueva (pestaña Actions → "App Android").
- La APK aparece en Releases del repositorio.
- Firma: la llave está cifrada en `signing.keystore.enc`; GitHub la descifra con el secreto `ANDROID_KEY_PASSWORD`.
- El contenido de la app (modelos, comparativas, diseño de pantallas) viene de la web: no hace falta nueva APK para eso.
