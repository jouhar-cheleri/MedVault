# import sqlalchemy

# engine = sqlalchemy.create_engine(
#     "mssql+pyodbc://DESKTOP-TOP2HSI/medvault?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes"
# )
# with engine.connect() as conn:
#     result = conn.execute(sqlalchemy.text("SELECT 1"))
#     print(result.scalar())

# In Python shell or a script
from app import db
db.drop_all()
db.create_all()