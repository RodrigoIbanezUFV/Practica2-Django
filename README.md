# Practica2 - Relecloud (Django)

Repositorio inicial para la práctica: arranque mínimo de una app Django preparada para CI/CD y despliegue.

## Contenido inicial
- Proyecto Django mínimo en `relecloud/`
- App de ejemplo `core/`
- `.env.example` con variables sensibles
- `requirements.txt` con dependencias básicas

## Ejecutar localmente (rápido)
1. python -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. cp .env.example .env  (rellenar valores)
5. python manage.py migrate
6. python manage.py runserver

## Notas
- No subir archivos `.env` ni secretos.
- Protege la rama `main` y añade pipeline para tests antes de merge.

## Arquitectura del Proyecto

Esta aplicación Django sigue una arquitectura modular con los siguientes componentes principales:

- **relecloud/**: Aplicación principal con modelos de destinos, cruceros y sistema de reviews
- **project/**: Configuración del proyecto Django
- **Pipeline CI/CD**: Automatización con Azure Pipelines (ver `azure-pipelines.yml`)
- **Base de datos**: PostgreSQL alojada en Azure

## Pipeline CI/CD

El proyecto utiliza Azure Pipelines para automatización continua:

1. **Build Stage**: Instalación de dependencias y ejecución de pruebas
2. **Deploy Stage**: Despliegue automático a Azure App Service

El pipeline se ejecuta automáticamente en cada push a `main` y en Pull Requests.

## Ejecutar Pruebas

Para ejecutar las pruebas unitarias localmente:

```bash
python manage.py test
```

Para ejecutar con cobertura:

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Estructura de Ramas

- `main`: Rama principal protegida
- `develop`: Rama de desarrollo (sincronizada con Azure DevOps)
- Feature branches: Cada PT (Paquete de Trabajo) se desarrolla en su propia rama

## Despliegue

La aplicación está desplegada en Azure App Service:
- **URL de producción**: https://rodrigoibanezcloud-brfmgaatdjb3grbt.spaincentral-01.azurewebsites.net/
- **Despliegue automático**: Via Azure Pipelines

## Equipo

Proyecto desarrollado por el Grupo B_3 para la asignatura Ingeniería del Software II - Universidad Francisco de Vitoria.

## Documentación Adicional

- **Wiki del proyecto**: Documentación técnica en Azure DevOps Wiki
- **Definition of Done**: Criterios de calidad en Azure DevOps Wiki
- **Backlog**: Gestión de tareas en Azure Boards
