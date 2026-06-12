# Relecloud — Web de turismo espacial (Django)
 
Aplicación web desarrollada con Django para una agencia ficticia de turismo
espacial, **ReleCloud**. Permite consultar destinos y cruceros, solicitar
información, registrarse e iniciar sesión, y dejar valoraciones sobre los
destinos visitados. Está desplegada en Azure App Service con integración y
despliegue continuo (CI/CD) mediante Azure Pipelines.
 
Proyecto desarrollado por el **Grupo B_3** para la asignatura **Ingeniería del
Software II** — Universidad Francisco de Vitoria.
 
---
 
## Funcionalidades
 
El proyecto implementa cuatro paquetes de trabajo (PT):
 
- **PT1 — Solicitud de información con envío de correo real.** El formulario de
  solicitud de información envía dos correos (notificación al administrador y
  confirmación al usuario) mediante SMTP.
- **PT2 — Imagen por destino.** Cada destino puede tener su propia imagen. Si no
  tiene, se muestra una imagen por defecto.
- **PT3 — Autenticación y reviews.** La autenticación se gestiona con
  django-allauth (registro, inicio y cierre de sesión). Los usuarios solo pueden
  valorar destinos o cruceros que tengan registrados como viajados, y se muestra
  la valoración media de cada destino.
- **PT4 — Orden por popularidad.** Los destinos se ordenan en la página principal
  por número de reviews y, en caso de empate, por valoración media.
---
 
## Tecnologías
 
- Python 3.11 / Django 4.2
- PostgreSQL (Azure Cosmos DB for PostgreSQL)
- django-allauth (autenticación)
- WhiteNoise (servir archivos estáticos)
- Azure App Service (despliegue)
- Azure Pipelines (CI/CD)
- Azure DevOps Boards y Wiki (gestión y documentación)
---
 
## Requisitos previos
 
- Python 3.11 o superior
- pip
- Acceso a la base de datos PostgreSQL del proyecto (credenciales por variable de
  entorno)
---
 
## Ejecución en local
 
1. Crear y activar un entorno virtual:
```
   python -m venv .venv
   .venv\Scripts\Activate.ps1      # Windows (PowerShell)
   source .venv/bin/activate       # Linux / macOS
```
 
2. Instalar las dependencias:
```
   pip install -r requirements.txt
```
 
3. Configurar las variables de entorno (ver sección siguiente).
4. Aplicar las migraciones:
```
   python manage.py migrate
```
 
5. Arrancar el servidor de desarrollo:
```
   python manage.py runserver
```
 
La aplicación quedará disponible en `http://127.0.0.1:8000/`.
 
---
 
## Variables de entorno
 
El proyecto lee la configuración sensible de variables de entorno. En local se
definen en la terminal; en producción, en la configuración del App Service de
Azure.
 
| Variable | Descripción |
|----------|-------------|
| `DB_PASSWORD` | Contraseña de la base de datos PostgreSQL. |
| `DEBUG` | `True` en local, `False` en producción (por defecto `False`). |
| `EMAIL_HOST_USER` | Cuenta de correo para el envío real (SMTP). |
| `EMAIL_HOST_PASSWORD` | Contraseña de aplicación del correo. |
| `ADMIN_EMAIL` | Dirección que recibe las notificaciones de solicitudes. |
 
> Las credenciales de correo solo son necesarias para el envío real. Sin ellas,
> el proyecto usa la consola para mostrar los correos, y en los tests usa un
> backend en memoria.
 
Ejemplo en PowerShell:
```
$env:DB_PASSWORD="..."
$env:DEBUG="True"
```
 
---
 
## Pruebas
 
El proyecto incluye una suite de pruebas automatizadas (unitarias y funcionales)
que cubre los cuatro paquetes de trabajo: envío de correo (PT1), imagen por
destino (PT2), autenticación con allauth y reviews (PT3) y orden por popularidad
(PT4).
 
Ejecutar las pruebas:
```
python manage.py test
```
 
Las pruebas usan una base de datos SQLite en memoria, por lo que no requieren
conexión a la base de datos de producción.
 
---
 
## Despliegue (CI/CD)
 
La aplicación se despliega automáticamente en Azure App Service mediante Azure
Pipelines (`azure-pipelines.yml`). El pipeline consta de dos etapas:
 
1. **Build:** instala dependencias, ejecuta las pruebas y recolecta los archivos
   estáticos (`collectstatic`).
2. **Deploy:** despliega el paquete en Azure App Service.
El pipeline se ejecuta en cada Pull Request y en cada integración a `main`. Solo
se despliega si las pruebas pasan.
 
- **URL de producción:** https://rodrigoibanezcloud-brfmgaatdjb3grbt.spaincentral-01.azurewebsites.net
---
 
## Estructura del proyecto
 
```
Practica2-Django/
├── project/            Configuración del proyecto Django (settings, urls, wsgi)
├── relecloud/          Aplicación principal (modelos, vistas, formularios, tests, plantillas)
├── requirements.txt    Dependencias del proyecto
├── azure-pipelines.yml Definición del pipeline CI/CD
└── manage.py
```
 
---
 
## Flujo de trabajo (Git)
 
- `main`: rama principal protegida. Solo se integra mediante Pull Request.
- Ramas de trabajo: cada paquete de trabajo (PT) y cada corrección se desarrolla
  en su propia rama (`feature/...`, `fix/...`), con su Pull Request, revisión de
  un compañero y comprobación del pipeline antes del merge.
---
 
## Documentación adicional (Azure DevOps Wiki)
 
- **Definition of Done:** criterios de calidad que debe cumplir cada PR.
- **Decisiones de diseño:** autenticación con allauth y criterio de orden por
  popularidad.
- **Problemas encontrados y soluciones:** registro técnico de las incidencias
  resueltas durante el desarrollo y el despliegue.
- **Backlog:** gestión de Epics, Features y PBIs en Azure Boards.
---
 
## Limitaciones conocidas
 
**Persistencia de imágenes en producción.** Las imágenes subidas por el operador
no persisten entre despliegues en Azure App Service, debido a que su sistema de
archivos es efímero (la carpeta `media/` se reinicia en cada despliegue). La
funcionalidad de PT2 funciona en local y está cubierta por tests. La solución
idónea sería un almacenamiento externo persistente (Cloudinary o Azure Blob
Storage). Ver la página "Problemas encontrados y soluciones" en la Wiki para más
detalle.
