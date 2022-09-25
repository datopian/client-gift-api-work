FROM python:3.8.12-alpine3.14

ENV APP_DIR=/srv/app

RUN apk add --update nodejs npm

RUN apk add tzdata \
        git \
        gettext \
        libmagic \
        curl \
        patch \
        sudo && \
    # Packages to build CKAN requirements and plugins
    apk add --virtual .build-deps \
        postgresql-dev \
        gcc \
        make \
        g++ \
        autoconf \
        automake \
		libtool \
        python3-dev \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
        openssl-dev \
        linux-headers

COPY requirements.txt /tmp/requirements.txt

# RUN pip install psycopg2-binary
RUN pip install  -r  /tmp/requirements.txt

RUN npm install -g os-types

COPY . ${APP_DIR}

ARG USER_ID=1001
ARG GROUP_ID=1001

RUN set -ex; \
  addgroup --gid $GROUP_ID --system containeruser; \
  adduser --system --uid $USER_ID -G containeruser containeruser; \
  chown -R containeruser:containeruser $APP_DIR
USER containeruser

WORKDIR ${APP_DIR}

CMD gunicorn --timeout 1200 -w 4 'server:app' --log-level LEVEL --bind 0.0.0.0:5000
