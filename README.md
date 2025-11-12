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