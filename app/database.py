from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQL_ALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# RAW Sql Connection with psycopg2
# while (
#     True
# ):  # İnternet veya bağlantı problemleri olursa bağlanana kadar yenilenmesi için döngü yaptık.
#     try:
#         connection = psycopg2.connect(
#             host="localhost",
#             database="fastapi",
#             user="postgres",
#             password="1234",
#             cursor_factory=RealDictCursor,
#         )
#         cursor = connection.cursor()
#         print("DB Connection successfull")
#         break
#     except Exception as error:
#         print("Connection to database failed")
#         print("Error:", error)
#         time.sleep(2)
