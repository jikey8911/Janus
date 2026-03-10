import sys
import os
sys.path.append(os.getcwd())

from app.db.session import engine, Base
from app.db.models import JobOffer, Proposal

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("Tablas creadas correctamente.")
