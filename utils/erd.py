from os import path

from alembic import command
from alembic.config import Config
from sqlalchemy_schemadisplay import create_schema_graph

from app.infra.database import engine, get_db_url, metadata

config = Config('/app/alembic.ini')
config.set_main_option('sqlalchemy.url', get_db_url())
command.upgrade(config, 'head')

graph = create_schema_graph(
    engine=engine,
    metadata=metadata,
    show_column_keys=True,
    show_datatypes=True,  # The image would get nasty big if we'd show the datatypes
    show_indexes=True,  # ditto for indexes
    rankdir='TB',  # From left to right OR top to bottom
    concentrate=False  # Don't try to join the relation lines together
)

output_file_path = path.join(path.dirname(__file__), '../docs_builder/_static', 'dbschema.png')
graph.write_png(output_file_path)  # write out the file
