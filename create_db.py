from db.database import Base, engine
from db import models

Base.metadata.create_all(bind=engine)
print("Database tables created.")