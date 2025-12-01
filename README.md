# Expense App

Aplicación para gestión de gastos.

## Requisitos Previos

1.  **Python 3.10+**
2.  **Tesseract OCR** (Necesario para escanear boletas)
    - Linux (Ubuntu/Debian): `sudo apt-get install tesseract-ocr`
    - macOS: `brew install tesseract`
    - Windows: Descargar instalador de [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

## Cómo ejecutar localmente (Sin Docker)

1.  **Crear y activar entorno virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar variables de entorno:**
    Asegúrate de tener un archivo `.env` en la raíz (puedes copiar `.env.example` si existe, o crear uno):
    ```env
    FLASK_APP=app.py
    FLASK_DEBUG=1
    SECRET_KEY=dev
    DATABASE_URL=sqlite:///instance/expense.db
    ```

4.  **Inicializar la base de datos (si es la primera vez):**
    ```bash
    python init_db.py
    ```

5.  **Ejecutar la aplicación:**
    ```bash
    python app.py
    ```
    O usando Flask:
    ```bash
    flask run --host=0.0.0.0 --port=5000
    ```

La aplicación estará disponible en `http://localhost:5000`.

## Solución de Problemas: Geolocalización en Móvil

Si al probar en el celular recibes el error **"No se pudo obtener la ubicación"**, es porque **los navegadores bloquean la geolocalización en sitios que no son HTTPS** (excepto localhost).

Para probar en el celular tienes dos opciones:

### Opción 1: Usar Ngrok (Recomendado)
Ngrok crea un túnel seguro (HTTPS) a tu servidor local.

1.  Descarga [ngrok](https://ngrok.com/download).
2.  Ejecuta tu app en una terminal: `python app.py`
3.  En **otra terminal**, ejecuta:
    ```bash
    ngrok http 5000
    ```
4.  Copia la URL que empieza con `https://...` y ábrela en tu celular.

### Opción 2: Certificado SSL Ad-hoc (Rápido)
Puedes forzar a Flask a usar HTTPS con un certificado temporal.

1.  Instala la dependencia necesaria:
    ```bash
    pip install pyopenssl
    ```
2.  Ejecuta Flask con modo certificado ad-hoc:
    ```bash
    flask run --host=0.0.0.0 --port=5000 --cert=adhoc
    ```
3.  Accede desde tu celular a `https://<TU_IP_LOCAL>:5000`.
    *Nota: El navegador te mostrará una advertencia de seguridad ("La conexión no es privada"). Debes dar clic en "Configuración avanzada" -> "Continuar de todos modos".*
