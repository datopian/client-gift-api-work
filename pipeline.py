import yaml
import requests
import os
import subprocess
from google.cloud import storage
from converter import datapackage2yml
from shutil import copyfile
import json


def update_fiscal_schema(org):
    org_directory = os.path.join(os.getcwd(), f'orgs/{org}')
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
    org_directory = os.path.join(os.getcwd(), f'orgs/{org}')

    org_path = os.path.abspath(f'orgs/{org}')
    if not os.path.isdir(f'{org_path}/data'):
        os.mkdir(f'{org_directory}/data')
    
    for resource in dpkg["resources"]:
        rname = f'gift-data/{owner_id}/{resource["hash"]}'
        lname = f"{org_directory}/data/{resource['name']}"

        blob = bucket.blob(rname)
        blob.download_to_filename(lname)


def runpipeline_subcommand(org):
    try:
        subprocess.call(["dpp", "run", "all"], cwd=f"./orgs/{org}")
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
    if not os.path.isdir(f'orgs/{org}'):
        os.mkdir(f'orgs/{org}')
        os.mkdir(f'orgs/{org}/data')

    org_path = os.path.abspath(f'orgs/{org}')
    copyfile(f'{os.getcwd()}/clean-data.py', f'{org_path}/clean-data.py' )
    datapackage2yml(dpkg, org_path)

def generate_org2(org, hashname):
    if not os.path.isdir(f'orgs/{org}'):
        os.mkdir(f'orgs/{org}')
        os.mkdir(f'orgs/{org}/data')
    
    org_path = os.path.abspath(f'orgs/{org}')
    copyfile(f'{os.getcwd()}/clean-data.py', f'{org_path}/clean-data.py' )

    gitstore_url = 'https://raw.githubusercontent.com/datopian/client-gift-api-work/main/opendpendingurl-dpkg.json'
    gitstore = requests.get(gitstore_url).json()
    dpkg_name = gitstore[f'{hashname}/{org}']
    # obtain datapackage from bucket
    storage_client = storage.Client()
    bucket_name = "gift-datasets"
    bucket = storage_client.get_bucket(bucket_name)
    rname = f'openspending/datastore.openspending.org/{dpkg_name}'
    blob = bucket.blob(rname)
    dpkg = json.loads(blob.download_as_string(client=None))
    # fetch table name
    tablenames_url = 'https://raw.githubusercontent.com/datopian/client-gift-api-work/main/openspendingtable.json'
    tablenames = requests.get(tablenames_url).json()[f'{hashname}/{org}']
    datapackage2yml(dpkg, org_path, tablenames)

    return dpkg


def cloud_storage_openspending(org, hashname, dpkg):
    storage_client = storage.Client()
    bucket_name = "gift-datasets"
    bucket = storage_client.get_bucket(bucket_name)

    org_directory = os.path.join(os.getcwd(), f'orgs/{org}')

    org_path = os.path.abspath(f'orgs/{org}')
    if not os.path.isdir(f'{org_path}/data'):
        os.mkdir(f'{org_directory}/data')
    
    for resource in dpkg["resources"]:
        rname = f'openspending/datastore.openspending.org/{hashname}/{org}/{resource["path"]}'
        lname = f"{org_directory}/data/{resource['name']}.csv"

        blob = bucket.blob(rname)
        blob.download_to_filename(lname)



if __name__== "__main__":
    org = "mexico"
    github_dpkg = f'https://raw.githubusercontent.com/gift-data/{org}/main/datapackage.json'
    dpkg = requests.get(github_dpkg).json()
    runpipeline_subcommand(org)
    # cloud_storage(dpkg,org)
    

