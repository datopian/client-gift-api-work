# API work for GIFT

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
