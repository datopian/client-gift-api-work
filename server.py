from flask import Flask
from sqlalchemy import create_engine
from babbage.manager import JSONCubeManager
from babbage.api import configure_api
from pipeline import (update_fiscal_schema, cloud_storage,
                      runpipeline_subcommand, generate_org,
                      generate_org2, cloud_storage_openspending )
import logging
import requests
import os

from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

app = Flask(__name__)
engine = create_engine(os.getenv('POSTGRES_CONNECTION_STR'))
models_directory = 'models/'
manager = JSONCubeManager(engine, models_directory)
blueprint = configure_api(app, manager)
app.register_blueprint(blueprint, url_prefix='/api/babbage/')

datasets_dir = os.environ['DATASETS_DIR']

@app.route('/api/pipeline/<org>')
def pipeline(org):
    """
    API call to start the pipeline
    for creating gift-api
    """
    print("START API PIPELINE")
    github_dpkg = f'https://raw.githubusercontent.com/gift-data/{org}/main/datapackage.json'
    dpkg = requests.get(github_dpkg).json()

    # check if organisation folder already exist
    org_path = os.path.abspath(f'{datasets_dir}/{org}')
    if (not os.path.isdir(org_path)):
        generate_org(datasets_dir, org, dpkg)

    # update fiscal YAML file
    update_fiscal_schema(datasets_dir, org)

    # download resources from google cloud
    print("Downloading resources from Google bucket")
    cloud_storage(datasets_dir, dpkg, org)

    # run datapackage-pipeline command line
    print("START PIPELINE SUBCOMMAND")
    runpipeline_subcommand(datasets_dir, org)

    return "done"


@app.route('/api/pipeline/openspending/<hashname>/<org>')
def pipeline_openspending(hashname, org):
    # Generate organization files
    dpkg = generate_org2(datasets_dir, org, hashname)
    # Fetch cloud storage data
    cloud_storage_openspending(org, hashname, dpkg)
    # run pipe line command line
    runpipeline_subcommand(org)
    return "done"


# if __name__ == '__main__':
#     app.run(host='0.0.0.0')

# app.run(host="localhost", port=3000, debug=True)
