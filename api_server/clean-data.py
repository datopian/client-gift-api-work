from datapackage_pipelines.wrapper import ingest, spew

params, datapackage, res_iter = ingest()

columns = params.get('columns')


def process_resource(_res_iter):
    for rows in _res_iter:
        def process_rows(_rows):
            for row in _rows:
                d = {}
                for k,v in row.items():
                    if k in columns:
                        if v:
                            d[k] = v
                        else:
                            d[k] = '0'
                    else:
                        d[k] = v
                yield d
        yield process_rows(rows)

spew(datapackage, process_resource(res_iter))
