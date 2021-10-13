import subprocess
import json

from babbage.api import model


# TODO: Should loop over all resources in the same way...
def main():
    # TODO: datapackage should come in as a dict (use existing function in upload_data.py)
    with open("datapackage.json") as f:
        datapackage = json.load(f)

    dataset_name = datapackage.get("name")
    dataset_hash = datapackage["resources"][0]["hash"][:63]
    model = generate_model_from_datapackage(
        datapackage, dataset_name, dataset_hash
    )
    write_model_to_json(model, dataset_hash)


def generate_model_from_datapackage(
    datapackage: dict, dataset_name: str, dataset_hash: str
) -> dict:
    """
    Generate a model for the dataset, returned as a string.

    Returns:
        dict:   Returns a dict with content on successful execution.
                Returns an empty dict on failure.
    """

    def print_error(message: str, error):
        print(f"Error: {message} - {type(error).__name__}: {error}")

    types_list = []

    try:
        schema = datapackage["resources"][0]["schema"][
            "fields"
        ]  # list of dicts
    except KeyError as e:
        message = (
            "The datapackage is not formatted as expected. Trying to access"
            "['resources'][0]['schema']['fields']"
        )
        print_error(message, error=e)
        return {}
    except IndexError as e:
        message = "The datapackage likely does not contain any resources..."
        print_error(message, error=e)
        return {}
    for field in schema:
        # All fields should have both properties, but just in case...
        if not (field.get("columnType") and field.get("name")):
            raise ValueError(
                "All fields should have both properties `type` and `name`"
            )
        types_list.append({"type": field["columnType"], "name": field["name"]})
    str_list = str(types_list)
    str_list = str_list.replace("'", '"')
    completed_process = subprocess.run(
        ["os-types", str_list], capture_output=True
    )

    # Process must go well to generate a model (return code = 0 → OK)
    if completed_process.returncode > 0:
        print(
            f"Error: Model generation failed for the dataset `{dataset_name}`."
            f" Reason: {str(completed_process.stdout)}",
        )
        return {}

    model_str = completed_process.stdout.strip().decode()
    model_dict = json.loads(model_str).get("model")
    # model_dict["fact_table"] = dataset_hash

    model_dict['profiles'] = {
        'fiscal': '*',
        'tabular': '*'
    }
    model_dict['@context'] = \
        'http://schemas.frictionlessdata.io/fiscal-data-package.jsonld'

    return model_dict


def write_model_to_json(model: dict, dataset_hash: str):
    with open(f"models/{dataset_hash}.json", "w") as f:
        json.dump(model, f, indent=2)


if __name__ == "__main__":
    main()
