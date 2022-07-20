FROM python:3.10
ENV PYTHONUNBUFFERED 1
ENV DATABASE_NAME analicap_db
ENV DATABASE_USER harlanv
ENV DATABASE_PASSWORD life2046
ENV DATABASE_HOST db
ENV DATABASE_PORT 3306

RUN mkdir /analicap
WORKDIR /analicap

# Installing OS Dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
libsqlite3-dev

RUN pip install -U pip setuptools

COPY requirements.txt /analicap/

RUN pip install -r /analicap/requirements.txt

ADD . /analicap/
# RUN pip install mysql-connector-python
# RUN pip install -r requirements.txt

# COPY run_app.sh .
# RUN ./run_app.sh

# Django service
EXPOSE 8000


# COPY run_app.sh .
# RUN ./run_app.sh

# RUN python manage.py runserver 0.0.0.0:8000