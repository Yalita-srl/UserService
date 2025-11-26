# User Service Microservice

This project is a simple, locally executable User Service for a delivery platform, built with Python, Django, and GraphQL. It provides basic CRUD functionality for users, JWT-based authentication, and role-based authorization.

---

## Opciones de Ejecución

Puedes ejecutar este proyecto de dos maneras:

1.  **Localmente con Python/Venv** (Ideal para desarrollo y pruebas rápidas).
2.  **Con Docker y NGINX** (Recomendado para un entorno de producción simulado y aislado).

---

## Opción 1: Ejecución Local (Python/Venv)

### 1. Prerrequisitos

-   Python 3.8+
-   Una instancia de servidor MySQL en ejecución (como XAMPP).
-   `pip` y `venv` para gestionar paquetes de Python.

### 2. Clonar el Repositorio

```bash
# Este paso ya está hecho si estás leyendo este archivo en el directorio del proyecto.
# git clone <repository-url>
# cd user-service
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (`user-service/`) copiando el archivo de ejemplo.

```bash
# Para Windows
copy .env.example .env
```

Abre el archivo `.env` y rellena tus datos de configuración, especialmente las credenciales de tu base de datos y una nueva `SECRET_KEY` de Django.

```ini
# .env
SECRET_KEY=tu-super-secreta-clave-aqui
DB_NAME=pedidos_user_service
DB_USER=root
DB_PASSWORD=tu_contraseña_mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 5. Configurar la Base de Datos MySQL

Inicia sesión en tu servidor MySQL y crea una nueva base de datos para el servicio.

```sql
CREATE DATABASE pedidos_user_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Ejecutar Migraciones de la Base de Datos

```bash
python manage.py migrate
```

### 7. Crear un Superusuario (Admin)

```bash
python manage.py createsuperuser
```

### 8. Ejecutar el Servidor de Desarrollo

```bash[sergioveloper@sergiodev yalita]$ curl GET http://localhost:8000/api/productos/1

python manage.py runserver
```

El servidor estará funcionando en `http://127.0.0.1:8000/`.

---

## Opción 2: Ejecución con Docker y NGINX

Esta opción conteneriza la aplicación, la base de datos y un proxy inverso NGINX.

### 1. Prerrequisitos

-   Docker y Docker Compose instalados.

### 2. Configurar Variables de Entorno para Docker

Abre tu archivo `.env` y ajústalo para que funcione con Docker. El `DB_HOST` debe apuntar al nombre del servicio de la base de datos en `docker-compose.yml` (en este caso, `db`).

```ini
# .env (ajustado para Docker)
SECRET_KEY=tu-super-secreta-clave-aqui
DB_NAME=pedidos_user_service
DB_USER=user
DB_PASSWORD=userpass
DB_HOST=db  # <-- ¡Importante! Apunta al servicio 'db' de Docker
DB_PORT=3306
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1,user-service # Añade 'user-service'
```

### 3. Migración de Datos desde XAMPP (Opcional)

Si tienes datos en tu base de datos local de XAMPP (`user_service`) que deseas mover al contenedor de Docker, sigue estos pasos:

**a. Exportar la base de datos desde XAMPP:**
Abre una terminal y ejecuta `mysqldump` para crear una copia de seguridad. Reemplaza `[ruta_a_mysql_bin]` y `[password]` si es necesario.

```bash
# Navega a la carpeta bin de tu instalación de MySQL en XAMPP
# cd C:\xampp\mysql\bin

# Ejecuta el comando de exportación
.\mysqldump -u root -p user_service > backup.sql
```
*Se te pedirá la contraseña de tu usuario `root` de MySQL.*

**b. Importar la base de datos al contenedor Docker:**
Una vez que los contenedores estén en funcionamiento (ver paso 4), ejecuta este comando desde la raíz del proyecto para importar el archivo `backup.sql` a la nueva base de datos del contenedor.

```bash
docker-compose exec -T db mysql -u user -puserpass pedidos_user_service < backup.sql
```

### 4. Construir y Ejecutar los Contenedores

Desde la raíz del proyecto (donde se encuentra `docker-compose.yml`), ejecuta el siguiente comando:

```bash
docker-compose up -d --build
```

-   `--build`: Reconstruye las imágenes si ha habido cambios en el `Dockerfile`.
-   `-d`: Ejecuta los contenedores en segundo plano (modo "detached").

### 5. Aplicar Migraciones en el Contenedor

La primera vez que inicies los contenedores, o después de cambios en los modelos, debes aplicar las migraciones de Django dentro del contenedor del servicio.

```bash
docker-compose exec user-service python manage.py migrate
```

### 6. Crear un Superusuario en el Contenedor (Opcional)

Si no migraste datos, puedes crear un nuevo superusuario en el contenedor.

```bash
docker-compose exec user-service python manage.py createsuperuser
```

¡Listo! El servicio ahora es accesible a través de NGINX en `http://localhost/graphql`.

---

## Cómo Probar la API

### Prueba a través de NGINX (Docker)

Usa Postman o tu cliente de API preferido para enviar peticiones a **`http://localhost/graphql`**.

### Prueba Local (Python/Venv)

Navega a la interfaz interactiva de GraphiQL en **`http://127.0.0.1:8000/graphql`**.

#### 1. Registrar un Nuevo Usuario

```graphql
mutation {
  registerUser(input: {
    email: "testuser@example.com",
    password: "strongpassword123",
    name: "Test User",
    phone: "1234567890",
    address: "123 Main St",
    role: "user"
  }) {
    user {
      id
      email
      name
      role
    }
  }
}
```

#### 2. Iniciar Sesión y Obtener un JWT

```graphql
mutation {
  tokenAuth(email: "testuser@example.com", password: "strongpassword123") {
    token
    user {
      id
      email
    }
  }
}
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMSIsImVtYWlsIjoidGVzdHVzZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoidXNlciIsImV4cCI6MTc2MzAxMTQ0Niwib3JpZ19pYXQiOjE3NjMwMDc4NDZ9.364zAu8qhizwc25zzjhpBC14F5ef7GVrAgXghhLoUUg

#### 3. Realizar Peticiones Autenticadas

Para realizar acciones autenticadas, pasa el `token` recibido en la cabecera HTTP `Authorization`.

```json
{
  "Authorization": "JWT eyJ0eXAiOiJKV1..."
}
```

#### 4. Obtener el Perfil de un Usuario (Autenticado)

```graphql
query {
  user(id: "1") {
    id
    name
    email
    phone
    address
    role
  }
}
```

#### 5. Listar Todos los Usuarios (Solo Admin)

```graphql
query {
  users(page: 1, limit: 5) {
    id
    email
    name
    role
  }
}
```

---
### 3. Resumen y Pasos Finales

Has recibido los siguientes archivos:

1.  `user-service/Dockerfile`: Define el entorno de ejecución para tu aplicación Django.
2.  `docker-compose.yml`: Orquesta los contenedores `user-service`, `db` y `nginx`. **Recuerda moverlo a la raíz del proyecto.**
3.  `nginx.conf`: Configura NGINX como proxy inverso. **Recuerda moverlo a la raíz del proyecto.**
4.  `README.md`: Instrucciones actualizadas.

**Para poner todo en marcha, sigue estos pasos:**

1.  **Mueve `docker-compose.yml` y `nginx.conf`** a la carpeta raíz `D:\2-2025\Microservicios\ProyectoFinalPedidos\`.
2.  **Ajusta tu archivo `.env`** como se indica en el nuevo `README.md` (lo más importante es `DB_HOST=db`).
3.  **(Opcional) Exporta tu base de datos** de XAMPP usando `mysqldump` si quieres conservar los datos.
4.  **Abre una terminal en la raíz del proyecto** (`ProyectoFinalPedidos`) y ejecuta `docker-compose up -d --build`.
5.  **Importa los datos** con `docker-compose exec -T db...` si realizaste el paso 3.
6.  **Aplica las migraciones** con `docker-compose exec user-service python manage.py migrate`.
7.  **Prueba el endpoint** en `http://localhost/graphql` usando Postman o una herramienta similar.

Con esto, tu microservicio está completamente dockerizado y listo para ejecutarse en un entorno aislado y reproducible.