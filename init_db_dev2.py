import sys
import os
sys.path.append(os.getcwd())

from infrastructure.adapters.db.session import engine, Base
from infrastructure.adapters.db.models import JobOffer, Proposal

print("Creando tablas en la base de datos (Estructura dev2)...")
Base.metadata.create_all(bind=engine)
print("Tablas creadas correctamente.")
