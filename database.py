from pony.orm import Database, Required, PrimaryKey, Optional
import datetime

db = Database()

class LogEventos(db.Entity):
    id = PrimaryKey(int, auto=True)
    descricao = Optional(str)
    tipo = Optional(str)
    data_criacao = Optional(datetime.datetime, default=datetime.datetime.now)
    usuario = Optional(str)

class Usuario(db.Entity):
    id = PrimaryKey(int, auto=True)
    username = Required(str, unique=True)
    hashed_password = Required(str)

db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
