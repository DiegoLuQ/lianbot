from fastapi import Request, Response, HTTPException
from .config import settings as sett
import asyncio
import jwt
import time

SECRET_KEY = sett.SECRET_KEY
# Diccionario para almacenar el recuento de solicitudes por número de celular
request_counts = {}

# Lista para almacenar los números de celular que han excedido el límite
exceeded_numbers = set()

BLOCK_DURATION_SECONDS_TOKEN = int(sett.BLOCK_DURATION_SECONDS_TOKEN) if sett.BLOCK_DURATION_SECONDS_TOKEN else 10
# Límite de solicitudes por hora
MAX_REQUESTS_PER_MINUTE = int(sett.MAX_REQUESTS_PER_MINUTE) if sett.MAX_REQUESTS_PER_MINUTE else 20
BLOCK_DURATION_MINUTES_FOR_REQUEST = float(sett.BLOCK_DURATION_MINUTES_FOR_REQUEST) if sett.BLOCK_DURATION_MINUTES_FOR_REQUEST else 0.5
        
def generate_jwt(number):
    payload = {
        "number": number,
        "exp": time.time() + (BLOCK_DURATION_SECONDS_TOKEN * 60)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")    
    
# Función para verificar si un usuario está bloqueado
def is_blocked(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["exp"] > time.time()
    except jwt.ExpiredSignatureError:
        return False  # El token ha expirado, el usuario no está bloqueado
    except jwt.InvalidTokenError:
        return False  # Token inválido, el usuario no está bloqueado  

def is_valid_token(token):
    try:
        # Decodificar y validar el token
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True  # El token es válido
    except jwt.ExpiredSignatureError:
        return False  # El token ha expirado
    except jwt.InvalidTokenError:
        return False  # El token no es válido

async def delete_token(number):
    try:
        await asyncio.sleep(30)
        request_counts[number] = 0
        print("El tiempo de espero a terminado.")
        print(request_counts)
    except Exception as e:
        print(e)

async def check_request_counts():
    try:
        
        while True:
            await asyncio.sleep(BLOCK_DURATION_MINUTES_FOR_REQUEST * 60)
            print("Verificando Solicitudes",request_counts)
            request_counts.clear()
            
            # await sleep(20)
            # print("Limpiando Solicitudes",request_counts)
    except Exception as e:
      print(e)
      
    
async def rate_limit(request: Request):
    try:
        body = await request.json()
        # Verificar si 'messages' está presente en el JSON
        if body['entry'][0]['changes'][0]['value']['messages'][0]['from']:
        # Ejecutar función para el json2
            number = body['entry'][0]['changes'][0]['value']['messages'][0]['from']
            numero_celular = number
            # print("Dentro de el primer if de rate_limit")
            request_count = request_counts.get(numero_celular, 0)
            # Inicializar token como None
            token = None
            # Verificar si se ha excedido el límite de solicitudes
            if request_count >= MAX_REQUESTS_PER_MINUTE:
                print("verificando usuario: ",request_counts)
                print("generando el token")
                token = generate_jwt(numero_celular)      
            # Actualizar el recuento de solicitudes del número de numero_celular
            request_counts[numero_celular] = request_count + 1
            # Retornar el token generado
            return token
        elif 'statuses' in body['entry'][0]['changes'][0]['value']:
            # Si hay 'statuses' en el JSON, retornar None
            pass
        else:
            # No se encuentra la clave 'messages', no hacer nada o manejar según sea necesario
            pass
    except KeyError as e:
        return ("KeyError:", e)  # Manejar KeyError y retornar None si se produce uno
    
async def check_blocked(request: Request, response: Response):
    token = request.cookies.get("token")

    if is_valid_token(token) and is_blocked(token):
        raise HTTPException(status_code=403, detail="Usuario bloqueado")
    elif not token:
        response.delete_cookie("token")  # Eliminar la cookie si no hay token