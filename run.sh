#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Aquí irían las migraciones de base de datos en el futuro
# alembic upgrade head

echo "Build and setup completed successfully."
