from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pony.orm import db_session, select, commit
from database import db, LogEventos, Usuario
from models import LogEventoCreate, LogEventoResponse
from auth import create_access_token, verify_password, get_password_hash
from datetime import timedelta
import uvicorn

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("startup")
@db_session
def seed_database():
    if LogEventos.select().count() == 0:
        print("Populando banco de dados com dados iniciais...")
        LogEventos(descricao="Sistema iniciado", tipo="INFO", usuario="admin")
        LogEventos(descricao="Primeira execução do sistema", tipo="INFO", usuario="admin")
        LogEventos(descricao="Erro de conexão detectado", tipo="ERROR", usuario="system")
        LogEventos(descricao="Conexão restaurada", tipo="INFO", usuario="system")
        LogEventos(descricao="Usuário logado", tipo="SUCCESS", usuario="user")
        commit()
        print("Banco de dados populado com sucesso.")

    if Usuario.select().count() == 0:
        print("Criando usuário admin...")
        Usuario(username="admin", hashed_password=get_password_hash("adminpass"))
        commit()
        print("Usuário admin criado com sucesso.")
        
        Usuario(username="user", hashed_password=get_password_hash("userpass"))
        commit()
        print("Usuário normal criado com sucesso.")
    else:
        print("Banco de dados já está populado com usuários.")


@app.post("/token")
@db_session
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = Usuario.get(username=form_data.username)
    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos!",
            header={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": usuario.username}, expires_delta=access_token_expires
    )
    print("DATA")
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/logeventos/", response_model=LogEventoResponse)
@db_session
async def create_log_evento(log_evento: LogEventoCreate, token: str = Depends(oauth2_scheme)):
    novo_log = LogEventos(
        descricao=log_evento.descricao,
        tipo=log_evento.tipo,
        usuario=log_evento.usuario,
    )
    commit()
    return LogEventoResponse(
        id=novo_log.id,
        descricao=novo_log.descricao,
        tipo=novo_log.tipo,
        data_criacao=novo_log.data_criacao,
        usuario=novo_log.usuario
    )


@app.get("/logeventos/", response_model=list[LogEventoResponse])
@db_session
def get_log_eventos(token: str=Depends(oauth2_scheme)):
    logeventos = select(le for le in LogEventos)[:]
    return [LogEventoResponse(
        id=le.id,
        descricao=le.descricao,
        tipo=le.tipo,
        data_criacao=le.data_criacao,
        usuario=le.usuario
    ) for le in logeventos]


@app.get("/logeventos/{log_id}",response_model=LogEventoResponse)
@db_session
def get_log_evento(log_id: int, token: str = Depends(oauth2_scheme)):
    log = LogEventos.get(id=log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log de Evento não encontrado.")
    return LogEventoResponse(
        id=log.id,
        descricao=log.descricao,
        tipo=log.tipo,
        data_criacao=log.data_criacao,
        usuario=log.usuario
    )


@app.put("/logeventos/{log_id}", response_model=LogEventoResponse)
@db_session
def update_log_evento(log_id: int, log_evento: LogEventoCreate, token: str = Depends(oauth2_scheme)):
    log = LogEventos.get(id=log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log de evento não encontrado")
    
    log.descricao = log_evento.descricao
    log.tipo = log_evento.tipo
    log.usuario = log_evento.usuario
    commit()  

    return LogEventoResponse(
        id=log.id,
        descricao=log.descricao,
        tipo=log.tipo,
        data_criacao=log.data_criacao,
        usuario=log.usuario
    )


@app.patch("/logeventos/{log_id}", response_model=LogEventoResponse)
@db_session
def patch_log_evento(log_id: int, log_evento: LogEventoCreate, token: str = Depends(oauth2_scheme)):
    log = LogEventos.get(id=log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log de evento não encontrado")
    
    if log_evento.descricao is not None:
        log.descricao = log_evento.descricao
    if log_evento.tipo is not None:
        log.tipo = log_evento.tipo
    if log_evento.usuario is not None:
        log.usuario = log_evento.usuario
    commit()  # Confirma as alterações no banco de dados

    return LogEventoResponse(
        id=log.id,
        descricao=log.descricao,
        tipo=log.tipo,
        data_criacao=log.data_criacao,
        usuario=log.usuario
    )


@app.delete("/logeventos/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
@db_session
def delete_log_evento(log_id: int, token: str = Depends(oauth2_scheme)):
    log = LogEventos.get(id=log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Log de evento não encontrado")
    
    log.delete()
    commit()
    return {"message": "Log de evento deletado com sucesso"}

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")
