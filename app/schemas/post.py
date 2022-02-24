from pydantic import BaseModel
from datetime import datetime
from .user import UserOut


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


# Neden şema kullanmalıyız? Şemanın avantajları :
#     - Data doğrulaması
#     - Client tarafından keyfe göre veri gönderilememesi, gönderilecek veri belirlediğimiz şemaya uygun olmalı
#     - Veriler önceden belirlediğimiz şemaya göre geleceği için gelen verileri işlerken onları teker teker bodyden almak zorunda kalmayız.
#     - Şema oluşturmada pydantic kütüphanesini kullanıyoruz, bu kütüphane FastAPI için özel bir kütüphane değil flask vb. başka kütüphanelerle de kullanılabilir.
