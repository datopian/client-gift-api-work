# API work for GIFT

## Production deployment

Set the following environment variables

- DATABASE_URL=postgresql://... - Postgres database URL
- GOOGLE_APPLICATION_CREDENTIALS - JSON credentials file for Google Cloud service user with bucket and storage object read access to the GIFT portal Giftless server's files
- BUCKET_NAME - Google Cloud Storage bucket for GIFT portal's Giftless server

Datapackage pipelines are dynamically set up in the `pipelines` directory - a subdirectory for each pipeline. It could be useful to mount this directory out of a docker container.

Babbage model JSON files define the babbage cube for each dataset. These are written to and read from the `models` directory. ***These should persist, so make sure to mount this directory out of the container if running in Docker.***


## Development setup

On Linux, you probably want to set the environment variables `USER_ID=$(id -u)`
and `GROUP_ID=$(id -g)` where you run docker-compose so that the container
shares your UID and GID. This is important for the container to have permission
to modify files owned by your host user (e.g. for python-black) and your host
user to modify files created by the container (e.g. migrations).

Configure GOOGLE_APPLICATION_CREDENTIALS and BUCKET_NAME using a .env file or something.

Run

    docker-compose up


## Developer notes

## `./`

* `model.py`: Investigating how to generate a model with https://github.com/openspending/datapackage-pipelines-fiscal (install it with `pip install datapackage-pipelines-fiscal`)

## `./api_server/`

* `./api_server/models/`: Directory containing JSON files that are read by the ["Babbage" API](https://github.com/openspending/babbage). The file `mexico.json` has the expected format for the API. We need to generate something like that.
* `./api_server/.env`: Should contain connection string for Postgres.
* `./api_server/models.py`: Testing with Babbage code. May not be useful.
* `./api_server/package.json`: Contains the dependency `os-types`, a command-line tool used to generate the "models".
* `./api_server/requirements.txt`: Requirements to run the Babbage API locally.
* `./api_server/upload_data.py`: Working script to download data from Google Storage (the resources stored in GIFT Portal) and upload them to a Postgres database (set up locally in this case).
* `./api_server/server.py`: Run the Babbage API locally.
