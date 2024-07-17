from fastapi import FastAPI, Query, Request, HTTPException, Depends, Response, Cookie
from config import settings as sett
from typing import Optional
from fastapi.responses import PlainTextResponse
import asyncio
from contextlib import asynccontextmanager
import httpx
import json

"""
Esta app servirá para
Enviar informes semanales del chatbot al usuario admin 
"""

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    try:
        # Aquí puedes iniciar tu tarea en segundo plano
        async def background_task():
            while True:
                print("Enviando ...")
                await recibir_mensaje_para_admin()  # Llama a tu función de envío de saludo
                await asyncio.sleep(sett.TIEMPO_PARA_ENVIAR_MSG_30SEG)  # Espera 30 segundos antes de enviar otro saludo
                # await asyncio.sleep(7 * 24 * 60 * 60)  # Espera 7 días antes de enviar otro saludo
                
        # Crea una tarea en segundo plano para la función background_task
        task = asyncio.create_task(background_task())

        # Continúa con el ciclo de vida de la aplicación
        yield

    finally:
        # Cancela la tarea en segundo plano al finalizar el contexto de la aplicación
        task.cancel()

app = FastAPI(lifespan=app_lifespan)

        
@app.post('/whatsapp')
async def recibir_mensaje_para_admin():
    try:

        number = sett.NUMERO_ADMIN
        #obtenemos la url de la imagen(informe) creada.
        url_img = await RecibirMensaje_supermain()
        #envio la url de la imagen al componente de ButtonImage
        new_data = await ButtonImage_Message(number, body="Enviando Informe", footer="Lw | Gracias por Preferirnos", options=["Cancelar Informe", "Otro", "Otro2"], url_img=url_img)
       
        print("services.administrar")
        await enviar_Mensaje_whatsapp(new_data)
        
        return 'EVENT_RECEIVED'   
      
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
def home():
    return {"hola":sett.token}

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
    

async def enviar_Mensaje_whatsapp(data):
    try:
        # print(data)
        print(data)
        whatsapp_token = sett.wsp_token
        whatsapp_url = sett.wsp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}

        async with httpx.AsyncClient() as client:
            response = await client.post(whatsapp_url, headers=headers, data=data)
        print(response.status_code)
        if response.status_code == 200:
            print('mensaje guardado', 200)
            return 'mensaje guardado', 200
        else:
            print("mensaje no enviado", response)
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return str(e), 403
  
async def enviar_mensaje_usuario(list_for):
    for item in list_for:
        await enviar_Mensaje_whatsapp(item)
        await asyncio.sleep(1)

async def RecibirMensaje_supermain():
    url = f"http://127.0.0.1:8002/generate_image"
    # url para imagen "http://127.0.0.1:8002/image/output5.jpeg"
    # whatsapp_token = sett.wsp_token
    async with httpx.AsyncClient() as client:
        # headers = {"Authorization": f"Bearer {whatsapp_token}"}
        # response = await client.get(url, headers=headers)
        response = await client.get(url)
        data = response.json()
        print(data)  
        return data.get("url_img", None)

async def ButtonImage_Message(number, body, footer, options, url_img):
    id_base = "unique-postback-id-"
    accion = {
        "buttons": []
    }
# Iterar sobre la lista de títulos de botones y crear botones correspondientes
    for i, titulo in enumerate(options, start=0):
        boton = {
            "type": "reply",
            "reply": {
                "id": f"{id_base}{i}",
                "title": titulo
            }
        }
        accion["buttons"].append(boton)

    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type":  "image",
                "image": {
                    "link": url_img
                }
            },
            "body": {
                "text": body
            },
            "footer": {
                "text": footer
            },
            "action": accion
        }
    })
    return data

def text_Message(number, text, messageId=None):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "context": {
            "message_id": messageId
        },
        "type": "text",
        "text": {
            "body": text
        },
        
    })
    return data
   
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1:8003", port=96)