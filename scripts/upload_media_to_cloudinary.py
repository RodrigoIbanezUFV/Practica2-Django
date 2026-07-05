"""
Sube a Cloudinary las imágenes de destinos que ya existen en la base de datos
y en la carpeta local `media/`, y actualiza el nombre almacenado en cada
registro para que `destination.image.url` apunte a la URL de Cloudinary.

Se ejecuta UNA sola vez (o cada vez que añadáis destinos nuevos sembrados por
fixtures/local). Requiere tener configuradas las variables de entorno de
Cloudinary, para que Django use `MediaCloudinaryStorage` como almacenamiento
por defecto:

    export CLOUDINARY_CLOUD_NAME=xxxx
    export CLOUDINARY_API_KEY=xxxx
    export CLOUDINARY_API_SECRET=xxxx
    # (y la BD que corresponda, p. ej. DB_PASSWORD si apuntáis a producción)

Uso:
    python scripts/upload_media_to_cloudinary.py
"""

import os
import sys

import django
from django.conf import settings
from django.core.files import File

# Permite ejecutar el script desde la raíz del repo.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from relecloud.models import Destination  # noqa: E402


def main():
    storage_backend = settings.DEFAULT_FILE_STORAGE
    if "cloudinary" not in storage_backend.lower():
        print(
            "ERROR: Django NO está usando Cloudinary como almacenamiento.\n"
            f"       DEFAULT_FILE_STORAGE = {storage_backend}\n"
            "       Define las variables CLOUDINARY_* antes de ejecutar el script."
        )
        sys.exit(1)

    media_root = settings.MEDIA_ROOT
    total = 0
    subidas = 0

    for destino in Destination.objects.exclude(image="").exclude(image__isnull=True):
        total += 1
        name = destino.image.name  # p. ej. "destinations/marte.jpg"
        local_path = os.path.join(media_root, name)

        if not os.path.exists(local_path):
            print(f"  [SKIP] {destino.name}: no existe el fichero local {local_path}")
            continue

        with open(local_path, "rb") as fh:
            # Re-guardar a través del storage por defecto (Cloudinary) sube el
            # fichero y deja el nombre del modelo sincronizado con Cloudinary.
            destino.image.save(name, File(fh), save=True)

        subidas += 1
        print(f"  [OK]   {destino.name}: {name} -> {destino.image.url}")

    print(f"\nHecho. {subidas}/{total} imágenes subidas a Cloudinary.")


if __name__ == "__main__":
    main()