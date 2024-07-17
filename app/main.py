from fastapi import FastAPI, Request, HTTPException, Depends, Response
from core.config import settings as sett
from fastapi.responses import PlainTextResponse
import lianbot_services as services
import re
from asyncio import create_task
from contextlib import asynccontextmanager
from core.request_token_management import (check_request_counts, rate_limit, check_blocked,
                                      request_counts, is_valid_token, delete_token, BLOCK_DURATION_SECONDS_TOKEN)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    try:
        # Inicializar el temporizador de desbloqueo para los números que ya están bloqueados
        print("Hola")

        create_task(check_request_counts())

        yield

    finally:
        # Limpiar los temporizadores y desbloquear los números al finalizar el contexto
        print("Fin")

app = FastAPI(lifespan=app_lifespan)


@app.post('/whatsapp', dependencies=[Depends(rate_limit), Depends(check_blocked)])
async def recibir_mensaje(request: Request, response: Response, token: str = Depends(rate_limit)):
    try:

        body = await request.json()

        display_number = body['entry'][0]['changes'][0]['value']['metadata']['display_phone_number']
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        messageId = message['id']
        
        contacts = value['contacts'][0]
        name = contacts['profile']['name']

        text = await services.obtener_Mensaje_whatsapp(message)
        timestamp = int(message['timestamp'])
    
        # print("whatsapp: ", body)
        # print("token: ", token)
        # print("Contando Solicitudes", request_counts)

        if is_valid_token(token):
            # Configurar la cookie con el token
            # print("token valido")
            response.set_cookie(
                key="token", value=token, expires=BLOCK_DURATION_SECONDS_TOKEN, httponly=True)
            print("services.bloquear")
            create_task(delete_token(number))
            await services.bloquear_usuario(text, number, messageId, name, timestamp, display_number)
            raise HTTPException(status_code=403, detail="Usuario bloqueado")
        else:
            print("services.administrar")

            await services.administrar_chatbot(text, number, messageId, name, timestamp, display_number)
            return 'EVENT_RECEIVED'

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get("/")
def home():
    return {"hola": sett.token}


@app.get("/whatsapp")
async def verify_token(request: Request):
    access_token = sett.token
    # Acceder directamente a los parámetros de consulta del objeto request
    hub_verify_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    try:
        if hub_verify_token and hub_challenge and hub_verify_token == access_token:
            # Devolver el challenge directamente como texto plano
            return PlainTextResponse(content=hub_challenge, status_code=200)
        else:
            raise HTTPException(status_code=400, detail="Invalid request")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=94)
