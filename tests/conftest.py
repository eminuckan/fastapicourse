import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app

from app.config import settings
from app.database import get_db
from app.database import Base
from app.oauth2 import create_access_token
from app import models

#  Conftest Dosyası fixtureların tanımlanığı dosyamız.
#  Fixturelar burada tanımlandıysa *** aynı klasörde(test modülünde) bulunan *** tüm test dosyalarında import edilmeden erişilebilirler.

SQL_ALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

""" 
    ! Bu fixture denen şerefsizler scope belirtilmezse her tekil testte çalışır bu da bazı durumlarda istemediğimiz bir şey. Çünkü her testten önce client
    ! fixture çalışıyor ve o ilk iş session fixture'ı çalıştırıyor. Session fixture test veritabanındaki tabloları silip tekrar oluşturuyor.
    ! Bu durumda user route testinde kullanıcı oluşturuluyor testi geçiyor ve sonraki login route testine geçerken tablolar silindiği için veritabanında kayıtlı
    ! kullanıcı olmuyor bu nedenle login testi başarısız oluyor.
    
    * FIXTURE SCOPES
        ? function: the default scope, the fixture is destroyed at the end of the test. (default)

        ? class: the fixture is destroyed during teardown of the last test in the class.

        ? module: the fixture is destroyed during teardown of the last test in the module.

        ? package: the fixture is destroyed during teardown of the last test in the package.

        ? session: the fixture is destroyed at the end of the test session.
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


""" 
    ! test_user Fixtrure'ı yazmamızın nedeni login testinin ilk kurduğumuz yapıda create_user testine bağımlı olmasıydı. Orada bir hata oluşunca
    ! login testi de hata veriyordu. Bu bir mantık hatasıydı. Bu yüzden loginden önce çalışan veritabanına bir kullanıcı ekleyen fixture eklemek 
    ! mantık hatamızı ortadan kaldırmanın yollarından biriydi.  
"""


""" 
    * Aslında bu test_user fixture'ı ileriyi düşünmeden yazılmış bir fixture.
    * Olması gereken test_posts fixture'ı gibi birden fazla user oluşturan bir fixture
    * Bu bir ders olduğu için ve önceden yazdığımız testleri teker teker düzeltmeyle uğraşmamak için yeni 
    * bir fixture yazıp sonrasında onu da kullandık.
"""


@pytest.fixture
def test_user(client):
    user_data = {"email": "test@webiyotik.com", "password": "123123"}

    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "test2@webiyotik.com", "password": "123123"}

    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(test_user, test_user2, session):
    post_data = [
        {"title": "1st title", "content": "1st content", "owner_id": test_user["id"]},
        {"title": "2nd title", "content": "2nd content", "owner_id": test_user["id"]},
        {"title": "3rd title", "content": "3rd content", "owner_id": test_user["id"]},
        {"title": "3rd title", "content": "3rd content", "owner_id": test_user2["id"]},
    ]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, post_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts


@pytest.fixture()
def test_vote(test_posts, session, test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user["id"])
    session.add(new_vote)
    session.commit()
