import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app

from app.config import settings
from app.database import get_db
from app.database import Base


SQL_ALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

""" 
    ! Bu fixture denen şerefsizler scope belirtilmezse her tekil testte çalışır bu da bazı durumlarda istemediğimiz bir şey. Çünkü her testten önce client
    ! fixture çalışıyor ve o ilk iş session fixture'ı çalıştırıyor. Session fixture test veritabanındaki tabloları silip tekrar oluşturuyor.
    ! Bu durumda user route testinde kullanıcı oluşturuluyor testi geçiyor ve sonraki login route testine geçerken tablolar silindiği için veritabanında kayıtlı
    ! kullanıcı olmuyor bu nedenle login testi başarısız oluyor.
    
    * FIXTURE SCOPES
        function: the default scope, the fixture is destroyed at the end of the test. (default)

        class: the fixture is destroyed during teardown of the last test in the class.

        module: the fixture is destroyed during teardown of the last test in the module.

        package: the fixture is destroyed during teardown of the last test in the package.

        session: the fixture is destroyed at the end of the test session.
    * FIXTURE SCOPES
"""


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    # run our code before we return our test
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    # -------------------------------------
    yield TestClient(app)
    # run our code after our test finishes
    # -------------------------------------
