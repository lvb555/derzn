FROM python:3.9-slim-buster
WORKDIR /app

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install

RUN apt-get install -y \
  dos2unix \
  libpq-dev \
  sqlite3 \
  libmariadb-dev-compat \
  libmariadb-dev \
  gcc \
  && apt-get clean

ENV SECRET_KEY=asdaaskdw9u2r4lfkjd32
ENV DEBUG=True
ENV ALLOWED_HOSTS='*'
ENV DB_URL=sqlite:///db.sqlite3
ENV BASE_URL=/
ENV EMAIL_HOST=localhost
ENV EMAIL_PORT=5822
ENV EMAIL_HOST_USER=admin
ENV EMAIL_HOST_PASSWORD=somepass
ENV EMAIL_USE_TLS=false
ENV EMAIL_USE_SSL=false

RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

RUN  ./manage.py makemigrations --merge --noinput

RUN ./manage.py makemigrations

# I'm not sure why this does not import any data into the database file
# but I'll leave it here in case someone would figure it out.
RUN ./manage.py migrate
RUN ./manage.py loaddata dump.json
