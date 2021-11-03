"""
This babbage model generation code
is extract from openspending-pipeline
https://github.com/openspending/datapackage-pipelines-fiscal
"""

from hashlib import md5
from slugify import Slugify
from datapackage_pipelines.generators import slugify
import requests
import json
from google.cloud import storage
import os


slugger = Slugify(separator="_", safe_chars="-.")

def dpkg_pipeline(org_name):
    github_dpkg = f'https://raw.githubusercontent.com/gift-data/{org_name}/main/datapackage.json'
    dpkg = requests.get(github_dpkg).json()

    generate_babbage(dpkg)

    with open(f'models/{org_name}.json', 'w') as outfile:
        json.dump(dpkg['babbageModel'], outfile)

def generate_babbage(dpkg):
    _, db_table, _ = extract_storage_ids(dpkg)

    source = dpkg["resources"][0]["schema"]
    kinds = sorted(set(
        f['columnType'].split(':')[0]
        for f in source['fields']
    ) - {'value'})

    resources = [
        slugify(kind, separator='_')
        for kind in kinds
    ]

    db_tables = dict(
        (res, '{}_{}'.format(db_table, i))
        for i, res in enumerate(resources)
    )
    db_tables[''] = db_table

    field_types = dict((x['slug'], x['type'])
                       for x in dpkg['resources'][-1]['schema']['fields'])

    bbg_hierarchies = {}
    bbg_dimensions = {}
    bbg_measures = {}

    ID_COLUMN_NAME = '_fdp__id_'
    model = dpkg["resources"][0]["model"]

    for hierarchy_name, h_props in model['dimensions'].items():
        hierarchy_name = slugify(hierarchy_name, separator='_')
        hierarchy = dict(
            label=hierarchy_name,
            levels=h_props['primaryKey']
        )
        bbg_hierarchies[hierarchy_name] = hierarchy

        # Get all hierarchy columns
        attributes = h_props['attributes']
        attributes = list(attributes.items())

        # Separate to codes and labels
        codes = dict(filter(lambda x: 'labelfor' not in x[1], attributes))
        labels = dict(map(lambda y: (y[1]['labelfor'], y[1]),
                            filter(lambda x: 'labelfor' in x[1], attributes)))
        
        # For each code, create a babbage dimension
        for fieldname, attribute in codes.items():
            dimension_name = fieldname

            bbg_attributes = {
                fieldname: dict(
                    column='.'.join([db_tables[hierarchy_name], fieldname]),
                    label=attribute.get('title', attribute['source']),
                    type=field_types[fieldname]
                )
            }
            bbg_dimension = dict(
                attributes=bbg_attributes,
                key_attribute=fieldname,
                label=attribute.get('title'),
                join_column=[hierarchy_name+'_id', ID_COLUMN_NAME]
            )

            label = labels.get(fieldname)
            if label is not None:
                fieldname = label['source']
                attribute = label
                bbg_attributes.update({
                    fieldname: dict(
                        column='.'.join([db_tables[hierarchy_name],
                                        fieldname]),
                        label=attribute.get('title', attribute['source']),
                        type=field_types[fieldname]
                    )
                })
                bbg_dimension.update(dict(
                    label_attribute=fieldname
                ))
            bbg_dimensions[dimension_name] = bbg_dimension

            for measurename, measure in model['measures'].items():
                    bbg_measures[measurename] = dict(
                        column=measurename,
                        label=measure.get('title', attribute['source']),
                        type=field_types[measurename]
                    )

            dpkg['babbageModel'] = dict(
                fact_table=db_tables[''],
                dimensions=bbg_dimensions,
                hierarchies=bbg_hierarchies,
                measures=bbg_measures
            )

def extract_names(source):
    title = source['title']
    dataset_name = source.get('name', title)
    dataset_name = slugger(dataset_name).lower()
    resource_name = source.get('resource-name', dataset_name)

    return title, dataset_name, resource_name

def extract_storage_ids(source):
    owner_id = source['id']
    _, dataset_name, _ = extract_names(source)
    dataset_id = '{}:{}'.format(owner_id, dataset_name)
    dataset_path = '{}/{}'.format(owner_id, dataset_name)
    dataset_name_hash = md5(dataset_name.encode('ascii')).hexdigest()[:16]
    db_table = '{}{}'.format(owner_id, dataset_name_hash)
    return dataset_id, db_table, dataset_path


def cloud_storage():
    storage_client = storage.Client()
    bucket_name = "gift-datasets"
    for blob in storage_client.list_blobs(bucket_name):
        print(blob)

if __name__ == "__main__":
    # print("IN HERE")
    # dpkg_pipeline("estimates-of-national-expenditure-2021-22")
    cloud_storage()