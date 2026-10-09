# Comparador OPPO

App para el equipo de ventas: compara modelos OPPO con la competencia, con
especificaciones, argumentos de venta, intereses del cliente, relojes,
auriculares y glosario de conceptos.

- La app se publica gratis con **GitHub Pages**.
- Los datos se guardan en **Firebase** (proyecto `versus-oppo`).
- Los vendedores entran sin contraseña. Solo el administrador puede editar.

## Contenido

- `index.html`: la app.
- `img/`: fotos de los dispositivos.
- `firestore.rules`: reglas de seguridad de la base de datos.

Los datos no están en este repositorio. Se cargan una vez con el archivo
`datos-completos.json` (ver paso 4).

## Puesta en marcha (una sola vez)

### 1. Firebase: activar el acceso del administrador
1. Entra en https://console.firebase.google.com y abre el proyecto **versus-oppo**.
2. Ve a **Authentication → Sign-in method**, activa **Correo electrónico/contraseña**
   y guarda.
3. En **Authentication → Users**, pulsa **Add user** y crea tu usuario (tu correo y
   una contraseña).
4. Copia el **User UID** que aparece en la lista.

### 2. Firebase: base de datos y reglas
1. Ve a **Firestore Database**. Si no está creada, pulsa **Crear base de datos**,
   elige la ubicación `eur3 (europe-west)` y el **modo de producción**.
2. Abre la pestaña **Reglas**, borra lo que haya y pega el contenido de
   `firestore.rules`.
3. Sustituye `PEGA_AQUI_TU_UID` por el UID que copiaste y pulsa **Publicar**.

### 3. GitHub Pages: publicar la app
1. En este repositorio, ve a **Settings → Pages**.
2. En **Source**, elige **Deploy from a branch**, rama `main` y carpeta `/ (root)`.
   Guarda.
3. Al cabo de un minuto o dos aparece la dirección de la app, del tipo
   `https://TU-USUARIO.github.io/comparador-oppo/`.
4. En Firebase, ve a **Authentication → Settings → Authorized domains**, pulsa
   **Add domain** y añade `TU-USUARIO.github.io`.

### 4. Cargar los datos
1. Abre la dirección de la app y pulsa **🔒 Acceso administrador**, al final de
   la página.
2. Entra con tu correo y tu contraseña.
3. Ve a **Administrar → Importar copia de seguridad** y elige el archivo
   `datos-completos.json`.
4. Espera a que aparezca el mensaje "Listo: … registros importados".

La app ya está lista. Comparte la dirección con los vendedores; para instalarla
en Android, usa "Añadir a pantalla de inicio" en Chrome.

## Notas
- Las fotos que subas desde la app se guardan comprimidas dentro de la base de
  datos, así que no hace falta tocar este repositorio para añadir modelos.
- Cualquiera que tenga el enlace puede ver los datos (igual que los vendedores).
- Para actualizar la app más adelante, basta con sustituir `index.html`.
