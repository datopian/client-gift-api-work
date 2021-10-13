# TODO: Need to test with datapackage.json that has more than one resource

import json
import os

import requests
from dotenv import load_dotenv
from frictionless import describe, Package



# TODO: This should be removed once the script is ready
# Overwrite datapackage.json with datapackage_copy.json to reset changes
# before running the script
import shutil
shutil.copyfile("datapackage_copy.json", "datapackage.json")


def main() -> None:
    load_dotenv()
    postgres_url = os.getenv("POSTGRES_CONNECTION_STR")

    google_cloud_base_url = (
        "https://storage.googleapis.com/gift-datasets/gift-data"
    )

    # Example with one data set
    datapackage_url = "https://raw.githubusercontent.com/gift-data/south-africa-national-estimates-2015-2019/main/datapackage.json"
    datapackage_path = "datapackage.json"

    # TODO: Uncomment following line
    # download_datapackage(datapackage_url)

    datapackage = load_datapackage(path=datapackage_path)
    # datapackage_schema = get_dataset_schema(datapackage)

    # TODO: Need to loop over all resources
    resource = datapackage["resources"][0]
    resource_url = get_resource_path(
        datapackage, resource, google_cloud_base_url
    )

    frictionless_resource = convert_resource_to_frictionless_format(
        resource_url
    )

    resource_schema = get_resource_schema(frictionless_resource)
    frictionless_resource = reset_schema_from_datapackage_resource(
        frictionless_resource, resource_schema
    )

    reset_resource_info_in_datapackage_json(
        resource_url, datapackage, datapackage_path
    )

    # TODO: Uncomment
    upload_resource_to_postgres(postgres_url, datapackage)


def download_datapackage(datapackage_url: str) -> None:
    response = requests.get(datapackage_url)
    with open("datapackage.json", "wb") as f:
        f.write(response.content)


def load_datapackage(path) -> dict:
    with open(path) as f:
        return json.load(f)


def get_dataset_schema(datapackage: dict) -> dict:
    return datapackage["resources"][0]["schema"]


def get_resource_path(
    datapackage: dict, resource: dict, google_cloud_base_url: str
) -> str:
    global GOOGLE_CLOUD_BASE_URL
    resource_name = resource["hash"]  # resource name is set by hash

    # URL-encode "=" char at the end
    dataset_id = datapackage["id"][:-1] + "%3D"

    resource_url = f"{google_cloud_base_url}/{dataset_id}/{resource_name}"
    return resource_url


def convert_resource_to_frictionless_format(resource_url: str) -> dict:
    # set format manually as it can't be inferred from the URL
    return describe(resource_url, format="csv")


def get_resource_schema(resource: dict) -> dict:
    return resource["schema"].to_dict()


def reset_schema_from_datapackage_resource(
    frictionless_resource: dict, resource_schema: dict
) -> dict:
    # match the column type to the description provided in the schema
    # in `datapackage.json`. Otherwise, Frictionless may infer types
    # incorrectly on its own
    for field in resource_schema["fields"]:
        frictionless_resource.schema.get_field(field["name"]).type = field["type"]  # type: ignore
    return frictionless_resource


# TODO: This should take the index of the resource to replace the correct one
def reset_resource_info_in_datapackage_json(
    resource_url: str, datapackage: dict, datapackage_path
) -> None:
    # Resource needs to be accessible to Frictionless, so set to publicly
    # accessible URL
    datapackage["resources"][0]["path"] = resource_url

    # The SQL table name is set to the "name" property
    # Take the first 63 characters, otherwise it raises the following error:
    # sqlalchemy.exc.IdentifierError
    datapackage["resources"][0]["name"] = datapackage["resources"][0]["hash"][:63]

    with open(datapackage_path, "w") as f:
        json.dump(datapackage, f)


# FIXME: the datapackage.json must contain accessible paths. Try setting
#        public Google URLs for the resources. Plan B could be to save
#        the resources locally and leave the paths unchanged but that's a lot
#        of unnecessary processing...
def upload_resource_to_postgres(postgres_url, datapackage_path):
    package = Package(datapackage_path)

    print("Uploading to PostgreSQL...")
    package.to_sql(postgres_url)


if __name__ == "__main__":
    main()
