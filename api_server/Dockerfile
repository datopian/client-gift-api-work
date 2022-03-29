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

RUN npm install -g os-types

# RUN mkdir -p /var/lib/gift-api
WORKDIR ${APP_DIR}

COPY . ${APP_DIR}

COPY requirements.txt ${APP_DIR}/requirements.txt


# RUN pip install psycopg2-binary
RUN pip install  -r  ${APP_DIR}/requirements.txt

CMD ["python", "server.py"]




