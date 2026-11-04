# MarcaSegura

Sistema web de control de asistencia con marcas geolocalizadas. Cada entrada o salida se valida contra el dispositivo del empleado y contra su última ubicación registrada. Cuando algo no cuadra, el sistema genera un incidente y avisa a los administradores por correo.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-SQLAlchemy-4479A1?logo=mysql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-Elastic%20Beanstalk-FF9900?logo=amazonaws&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)

---

## Qué hace

**Para el empleado**
- Marca entrada y salida desde el navegador. El sistema alterna el tipo de marca automáticamente según la última registrada.
- Cada marca envía la ubicación (latitud, longitud y precisión del GPS) y un identificador único del dispositivo.

**Para el administrador**
- Gestiona usuarios, roles, estado y horario de entrada y salida.
- Autoriza o bloquea los dispositivos desde los que marca cada empleado.
- Consulta la bitácora de auditoría y los incidentes, clasificados por severidad.

**Controles de seguridad automáticos**

| Situación | Respuesta del sistema | Severidad |
| --- | --- | --- |
| Marca desde un dispositivo bloqueado | Rechaza la marca (403) y registra un incidente | Alta |
| Marca desde un dispositivo de otro empleado | Rechaza la marca (403) y registra un incidente | Alta |
| 5 intentos fallidos de inicio de sesión | Registra un incidente y notifica a los administradores | Alta |
| Desplazamiento físicamente imposible entre dos marcas | Acepta la marca, registra un incidente y notifica a los administradores | Media |
| Primer uso de un dispositivo nuevo | Lo registra como conocido, pendiente de autorización | — |

## Detección de ubicaciones anómalas

Para cada marca nueva se calcula la distancia a la marca anterior con la fórmula de Haversine y se divide entre el tiempo transcurrido. Si la velocidad resultante supera los **200 km/h**, el desplazamiento se considera poco realista. Las diferencias menores a **5 km** se ignoran para no generar falsos positivos por el ruido normal del GPS.

Ambos umbrales están en `app/services/location_service.py`.

## Arquitectura

```mermaid
flowchart LR
    U[Navegador del empleado<br>geolocalización + UUID del dispositivo] -->|POST /attendance/mark<br>JWT en cookie + CSRF| R

    subgraph Flask
        R[Blueprints<br>auth · attendance · users · audit] --> S[Servicios<br>auth · attendance · device<br>location · incident · email]
        S --> M[Modelos SQLAlchemy<br>User · Mark · Device · Incident]
    end

    M --> DB[(MySQL)]
    S --> E[SMTP<br>alertas a administradores]
```

La aplicación sigue el patrón *application factory* de Flask. Las rutas solo validan la petición y la respuesta; la lógica de negocio vive en la capa de servicios, lo que permite probarla de forma aislada.

### Decisiones de diseño

- **JWT en cookies HttpOnly con protección CSRF** en vez de tokens en headers: el token no es accesible desde JavaScript y los formularios quedan protegidos contra CSRF.
- **Identificador de dispositivo persistente** generado con `crypto.randomUUID()` en el navegador, para asociar cada marca a un dispositivo concreto.
- **Migraciones versionadas con Alembic**, de modo que el esquema evoluciona igual en local y en producción.
- **Configuración por variables de entorno**: ningún secreto vive en el repositorio.
- **Zona horaria de Costa Rica** explícita en los timestamps, normalizada al comparar con valores leídos de MySQL.

## CI/CD

Cada push a `main` ejecuta el pipeline de `.github/workflows/deploy.yml`:

```mermaid
flowchart LR
    A[Push a main] --> B[Instalar dependencias<br>Python 3.12]
    B --> C[pytest]
    C -->|pruebas en verde| D[Credenciales temporales<br>rol IAM vía OIDC]
    D --> E[eb deploy<br>AWS Elastic Beanstalk]
    C -.->|alguna falla| X[El despliegue se detiene]
```

GitHub Actions obtiene credenciales temporales de AWS asumiendo un rol IAM mediante OpenID Connect. No hay llaves de acceso guardadas como secretos. En producción la app corre en Elastic Beanstalk (Amazon Linux 2023) con Gunicorn.

## Tecnologías

| Capa | Herramientas |
| --- | --- |
| Backend | Python 3.12, Flask 3, Flask-JWT-Extended, Flask-Mail |
| Datos | MySQL, SQLAlchemy 2, Flask-Migrate (Alembic), PyMySQL |
| Frontend | Plantillas Jinja2, JavaScript (Geolocation API) |
| Pruebas | pytest, SQLite en memoria |
| Infraestructura | AWS Elastic Beanstalk, Gunicorn, GitHub Actions, IAM con OIDC |

## Estructura del proyecto

```
app/
├── config/        # Configuración y extensiones (db, jwt, mail, migrate)
├── models/        # User, Mark, Device, Incident
├── routes/        # Blueprints: web_auth, attendance, users, audit
├── services/      # Lógica de negocio y decoradores de autorización
├── templates/     # Vistas de administrador, empleado y login
└── static/
migrations/        # Historial de migraciones Alembic
tests/             # Pruebas con pytest
create_admin.py    # Script para crear el primer administrador
run.py             # Punto de entrada en desarrollo
Procfile           # Arranque con Gunicorn en Elastic Beanstalk
```

## Cómo correrlo en local

**Requisitos:** Python 3.12 y un servidor MySQL.

```bash
# 1. Clonar e instalar dependencias
git clone https://github.com/ozco26/MarcaSegura.git
cd MarcaSegura
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configurar variables de entorno
cp .env.example .env            # y completa los valores

# 3. Crear las tablas
flask --app run.py db upgrade

# 4. Crear el primer administrador
python create_admin.py

# 5. Levantar la aplicación
python run.py
```

La app queda en `http://127.0.0.1:5000/login`.

### Variables de entorno

| Variable | Descripción |
| --- | --- |
| `SECRET_KEY` | Clave secreta de Flask |
| `JWT_SECRET_KEY` | Clave para firmar los tokens JWT |
| `DATABASE_URL` | Cadena de conexión, p. ej. `mysql+pymysql://usuario:clave@localhost/marcasegura` |
| `JWT_COOKIE_SECURE` | `True` en producción (solo HTTPS) |
| `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS` | Servidor SMTP para las alertas |
| `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` | Credenciales y remitente del correo |

## Pruebas

```bash
pytest -v
```

La suite usa SQLite en memoria, así que no necesita MySQL ni variables de entorno. Cubre autenticación y bloqueo por intentos fallidos, registro de marcas, gestión de dispositivos y auditoría (42 pruebas).

## Endpoints principales

| Método | Ruta | Acceso | Descripción |
| --- | --- | --- | --- |
| GET, POST | `/login` | Público | Inicio de sesión |
| GET | `/dashboard` | Autenticado | Panel según el rol |
| POST | `/attendance/mark` | Empleado | Registra una marca con ubicación y dispositivo |
| GET, POST | `/admin/users/` | Administrador | Crear y editar usuarios |
| POST | `/admin/users/delete/<id>` | Administrador | Eliminar usuario |
| GET | `/admin/audit/` | Administrador | Bitácora de marcas y dispositivos |
| POST | `/admin/audit/device/<id>/authorize` | Administrador | Autorizar dispositivo |
| POST | `/admin/audit/device/<id>/block` | Administrador | Bloquear dispositivo |
| GET | `/admin/audit/incidents` | Administrador | Incidentes de seguridad |

---

Desarrollado por **José Pablo Orozco Salas** como proyecto académico de Ingeniería Informática (ULACIT, 2026).
[LinkedIn](https://www.linkedin.com/in/jos%C3%A9-pablo-orozco-salas-8b766bb8/) · [GitHub](https://github.com/ozco26)
