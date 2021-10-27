from flask import Flask
from sqlalchemy import create_engine
from babbage.manager import JSONCubeManager
from babbage.api import configure_api

app = Flask('demo')
engine = create_engine('postgresql://steveoni@localhost/testing')
models_directory = 'models/'
manager = JSONCubeManager(engine, models_directory)
blueprint = configure_api(app, manager)
app.register_blueprint(blueprint, url_prefix='/api/babbage/')

# This code block was inserted to test whether we retrieve data from the DB
from sqlalchemy.sql import select, text
conn = engine.connect()
# table name needs to be quoted so it works with dashes
s = select([text('* FROM "5a25dc2b975eb85bb58a44a3a206d85c17b0f3fe35167d9ba535b5c15421be1"')])
result = conn.execute(s)
print(result.fetchone())

app.run()
