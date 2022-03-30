from datapackage_pipelines.wrapper import ingest, spew
import  logging
import requests
params, datapackage, res_iter = ingest()

columns = params.get('columns')
column_types = params.get('types')
osTypes = requests.get('https://raw.githubusercontent.com/openspending/os-types/master/src/os-types.json').json()

column_and_types = {k:v for k, v in list(zip(columns,column_types))}
log = logging.getLogger(__name__)

def process_resource(_res_iter):
    
    for rows in _res_iter:
        def process_rows(_rows):
            for row in _rows:
                d = {}
                for k,v in row.items():
                    if k in columns:
                        if v != None:
                            d[k] = v
                        else:
                            coltype = column_and_types[k]
                            dataType  = osTypes[coltype]['dataType']
                            if dataType == 'string':
                                d[k] = '0'
                            else:
                                d[k] = 0
                    else:
                        d[k] = v
                yield d
        yield process_rows(rows)

spew(datapackage, process_resource(res_iter))
