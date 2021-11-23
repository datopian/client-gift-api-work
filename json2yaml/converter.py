import json
import yaml

fname = "datapackage.json"

base_data = json.load(open(fname,"r"))

data = {}
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
            data_source["url"] = f"/data/{source['name']}"
            data_source["encoding"] = source['encoding']
            data['sources'].append(data_source)

        fields = value[0]['schema']['fields']
        data['fields'] = []
        for field in fields:
            data_field = {}
            data_field['header'] = field['title']
            data_field['columnType'] = field['columnType']

            if len(field['options']) > 0:
                data_field['options'] = {
                    'groupChar': field['groupChar'],
                    'decimalChar': field["decimalChar"]
                }
            else:
                data_field['options'] = {}
            data['fields'].append(data_field)

yaml.dump(data, open("test_spec.yml","w"),sort_keys=False)
    





