import yaml
import requests
import os
import subprocess
from google.cloud import storage
from converter import datapackage2yml
from shutil import copyfile

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =  '/Users/steveoni/Downloads/gift-data-110ad1f62153.json'


def update_fiscal_schema(org):
    org_directory = os.path.join(os.getcwd(), org)
    org_yml = org_directory + "/fiscal.source-spec.yaml"
    github_dpkg = f'https://raw.githubusercontent.com/gift-data/{org}/main/datapackage.json'
    dpkg = requests.get(github_dpkg).json()

    fiscal_yml = yaml.safe_load(open(org_yml, "rb"))
    fiscal_yml["sources"] = []
    for source in dpkg["resources"]:
        data_source = {}
        data_source["url"] = f"./data/{source['name']}"
        data_source['encoding'] = source['encoding']
        fiscal_yml["sources"].append(data_source)

    yaml.dump(fiscal_yml, open(org_yml, "w"), sort_keys=False)


def cloud_storage(dpkg,org):
    storage_client = storage.Client()
    bucket_name = "gift-datasets"
    bucket = storage_client.get_bucket(bucket_name)

    owner_id = dpkg["id"]
    org_directory = os.path.join(os.getcwd(), org)

    os.mkdir(f'{org_directory}/data')
    for resource in dpkg["resources"][:2]:
        rname = f'gift-data/{owner_id}/{resource["hash"]}'
        lname = f"{org_directory}/data/{resource['name']}"

        blob = bucket.blob(rname)
        blob.download_to_filename(lname)


def runpipeline_subcommand(org):
    try:
        subprocess.call(["dpp", "run", "all"], cwd=f"./{org}")
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise(e)


def generate_org(org, dpkg):
    """
    Generate organisation folder
    containing all neccessary files for
    creating api pipeline
    """

    # create directory
    os.mkdir(org)
    os.mkdir(f'{org}/data')

    org_path = os.path.abspath(org)
    copyfile(f'{os.getcwd()}/clean-data.py', f'{org_path}/clean-data.py' )
    datapackage2yml(dpkg, org_path)


if __name__== "__main__":
    org = "mexico"
    github_dpkg = f'https://raw.githubusercontent.com/gift-data/{org}/main/datapackage.json'
    dpkg = requests.get(github_dpkg).json()
    runpipeline_subcommand(org)
    # cloud_storage(dpkg,org)
    

