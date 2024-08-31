from litestar.contrib.sqlalchemy.plugins import SQLAlchemySyncConfig, SQLAlchemyPlugin

from app.models import Base

db_config = SQLAlchemySyncConfig(
    connection_string="sqlite:///shacketons_db.sqlite3",
    metadata=Base.metadata,
    create_all=True,
)
db_plugin = SQLAlchemyPlugin(db_config)