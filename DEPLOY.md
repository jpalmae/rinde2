# Guía de Despliegue (Deployment)

Esta guía explica cómo subir y desplegar la aplicación "Expense App".

## Opciones de Despliegue

### 1. Render / Railway (Recomendado)

Estas plataformas detectan automáticamente aplicaciones Python y son muy fáciles de configurar.

**Pasos:**

1.  Sube tu código a un repositorio de **GitHub**.
2.  Crea una cuenta en [Render](https://render.com) o [Railway](https://railway.app).
3.  Conecta tu cuenta de GitHub y selecciona el repositorio.
4.  La plataforma detectará el archivo `requirements.txt` y el `Procfile` automáticamente.
5.  **Configuración de Variables de Entorno:**
    En el panel de control de la plataforma, agrega las variables definidas en tu `.env` (excepto `FLASK_DEBUG` que debe ser `False` o no estar):
    - `SECRET_KEY`: Genera una clave segura.
    - `DATABASE_URL`: Si usas una base de datos externa (PostgreSQL es recomendado para producción). Si usas SQLite, ten en cuenta que los datos se perderán cada vez que la app se reinicie en estas plataformas (sistema de archivos efímero).
    - `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`: Para el envío de correos.

**Nota sobre SQLite:**
Por defecto, esta app usa SQLite. En plataformas como Render/Heroku, el sistema de archivos es efímero. Esto significa que si la app se reinicia, **se borra la base de datos**. Para producción real, se recomienda usar PostgreSQL. Render y Railway ofrecen bases de datos PostgreSQL gestionadas que puedes conectar fácilmente cambiando la variable `DATABASE_URL`.

### 2. Docker

Si prefieres usar contenedores, se ha incluido un `Dockerfile`.

**Construir la imagen:**
```bash
docker build -t expense-app .
```

**Correr el contenedor:**
```bash
docker run -p 5000:5000 --env-file .env expense-app
```

### 3. Servidor VPS (DigitalOcean, AWS EC2, etc.)

1.  Clona el repositorio en el servidor.
2.  Instala las dependencias del sistema:
    ```bash
    sudo apt-get update
    sudo apt-get install python3-pip tesseract-ocr
    ```
3.  Crea un entorno virtual e instala dependencias:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
4.  Configura las variables de entorno en un archivo `.env`.
5.  Ejecuta con Gunicorn (o configura un servicio systemd):
    ```bash
    gunicorn --bind 0.0.0.0:8000 "app:create_app()"
    ```
6.  Configura Nginx como proxy reverso hacia el puerto 8000.

## Requisitos del Sistema

La aplicación requiere `tesseract-ocr` para el procesamiento de imágenes (OCR).
- El `Dockerfile` ya lo incluye.
- En servidores Linux (Debian/Ubuntu), instalar con `sudo apt-get install tesseract-ocr`.
