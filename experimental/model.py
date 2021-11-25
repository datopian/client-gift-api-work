import os
import json
import logging
import subprocess
import sys

from datapackage_pipelines.wrapper import ingest, spew


with open("datapackage.json") as f:
    datapackage = json.load(f)


# os_types = params['os-types']
# options = {}
# titles = {}

resource = datapackage['resources'][0]
fields = resource['schema']['fields']

limited_fields = []

for field in fields:
    field.pop("slug", None)
    field.pop("groupChar", None)
    field.pop("decimalChar", None)
    field.pop("conceptType", None)
    field["type"] = field["columnType"]
    del field["columnType"]
    field["options"] = []

    limited_fields.append({"type": field["type"], "name": field["name"]})

# print(limited_fields)
fields = limited_fields
# exit()

# for field in fields:
#     field_name = field['name']
#     # if field_name not in os_types:
#     #     logging.error('Missing OS Type for field %s', field_name)
#     field['type'] = os_types[field_name]
#     field['options'] = options.get(field_name, {})
#     if field_name in titles:
#         field['title'] = titles[field_name]

# Try skipping this step
result = subprocess.run(['/usr/bin/env', 'os-types', json.dumps(fields)],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        env=os.environ.copy())

print(result)

errors = result.stderr.decode('utf8')
if len(errors) > 0:
    raise RuntimeError(errors)
output = result.stdout.decode('utf8')
if output.startswith('FAILED'):
    raise RuntimeError(output)

model = json.loads(output)
if 'unknown' in model['model'].get('dimensions', {}):
    model['model']['dimensions'].pop('unknown')

datapackage['model'] = model['model']

for field in fields:
    field.update(model['schema']['fields'][field['name']])
    if 'options' in field:
        del field['options']

resource['schema']['primaryKey'] = model['schema']['primaryKey']

datapackage['profiles'] = {
    'fiscal': '*',
    'tabular': '*'
}
datapackage['@context'] = \
    'http://schemas.frictionlessdata.io/fiscal-data-package.jsonld'

spew(datapackage, [])
