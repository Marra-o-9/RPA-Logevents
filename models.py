from pydantic import BaseModel
import datetime

class LogEventoCreate(BaseModel):
    descricao: str
    tipo: str
    usuario: str

class LogEventoResponse(BaseModel):
    id: int
    descricao: str
    tipo: str
    data_criacao: datetime.datetime
    usuario: str
