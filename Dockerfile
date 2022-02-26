FROM python:3.9.9

WORKDIR /usr/src/app

COPY requirements.txt ./

# COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# COPY . /usr/src/app/

CMD [ "uvicorn","app.app:app","--host","0.0.0.0","--port","8000" ]