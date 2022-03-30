import json
import yaml

def datapackage2yml(base_data, org_path, tb_name=None):
    data = {}
    keys  = list(base_data.keys())
    if "id" not in keys:
        data['owner-id'] = tb_name[:40]
    for key, value in base_data.items():
        if key == "name":
            data["title"] = value
            data["dataset-name"] = value
            data["resource-name"] = value

        elif key == "id":
            data["owner-id"] = value
        elif key == "resources":
            data['sources'] = []
            for source in value:
                data_source = {}
                data_source["url"] = f"./data/{source['name']}"
                if 'csv' not in data_source["url"]:
                    data_source["url"] = f'{data_source["url"]}.csv'
                data_source["encoding"] = source['encoding']
                data['sources'].append(data_source)

            fields = value[0]['schema']['fields']
            data['fields'] = []
            for field in fields:
                data_field = {}
                data_field['header'] = field['name'] if 'name' in field else field['title']
                data_field['columnType'] = field['columnType'] if 'columnType' in field else field['osType']

                if 'part' in data_field['columnType']:
                    data_field['columnType'] = data_field['columnType'].split(":part")[0]
                if 'options' in field:
                    if len(field['options']) > 0:
                        data_field['options'] = {
                            'groupChar': field['groupChar'],
                            'decimalChar': field["decimalChar"]
                        }
                    else:
                        data_field['options'] = {}
                else:
                    data_field['options'] = {}
                    if 'decimalChar' in field:
                        data_field['options']['decimalChar'] = field["decimalChar"]
                    if 'groupChar' in field:
                        data_field['options']['groupChar'] = field["groupChar"]
                data['fields'].append(data_field)

    data['deduplicate'] = True
    data['postprocessing'] = [{
        'processor': 'clean-data',
        'parameters': {
            'columns': [d['header'] for d in data['fields']],
            'types': [d['columnType'] for d in data['fields']]
        }
    }]

    yaml.dump(data, open(f"{org_path}/fiscal.source-spec.yaml","w"),sort_keys=False)
    





