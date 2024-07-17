from pathlib import Path
from dotenv import load_dotenv
from os import environ

"""
TENEMOS CONFIGURADO NUESTRAS VARIABLES DE ENTORNO
"""

env_path = Path('.') / '.env'

load_dotenv(dotenv_path=env_path)


class Settings:
    token = environ.get('token_access')
    wsp_url = environ.get('WSP_URL')
    wsp_token = environ.get('TOKEN_WSP')
    doc_pdf = environ.get("DOC_PDF")
    SECRET_KEY = environ.get('SECRET_KEY')
    
    # Bloquear y/o Suspender Mensajes
    BLOCK_DURATION_SECONDS_TOKEN = environ.get("BLOCK_DURATION_SECONDS_TOKEN")
    MAX_REQUESTS_PER_MINUTE = environ.get("MAX_REQUESTS_PER_MINUTE")
    BLOCK_DURATION_MINUTES_FOR_REQUEST = environ.get("BLOCK_DURATION_MINUTES_FOR_REQUEST")
    
    #REDIS
    DURATION_REDIS_FLUJO = environ.get("DURATION_REDIS_FLUJO")
    
    # Admin para enviar informes
    NUMERO_ADMIN = environ.get("NUMERO_ADMIN")
    TIEMPO_PARA_ENVIAR_MSG_7DIAS = environ.get('TIEMPO_PARA_ENVIAR_MSG_7DIAS')
    TIEMPO_PARA_ENVIAR_MSG_30SEG = environ.get('TIEMPO_PARA_ENVIAR_MSG_30SEG')
    
    #DB MYSQL
    DB_MYSQL = environ.get("DB_MYSQL")
    DB_MONGO = environ.get("DB_MONGO")
    DB_MONGO_COMPAS = environ.get("DB_MONGO_COMPAS")
    DB_MONGODOCKER=environ.get("DB_MONGODOCKER")
    DB_MONGO_LOCAL=environ.get("DB_MONGO_LOCAL")
    API_WSP_MONGO=environ.get("API_WSP_MONGO")
    DB_REDIS=environ.get("DB_REDIS")
    DB_REDIS_PORT=environ.get("DB_REDIS_PORT")
    
    #FACEBOOK
    FB_URL  = environ.get("FB_URL")
    
    stickers = {
    "mort":381731608015965,
    "poyo_feliz": 984778742532668,
    "perro_traje": 1009219236749949,
    "perro_triste": 982264672785815,
    "pedro_pascal_love": 801721017874258,
    "pelfet": 3127736384038169,
    "anotado": 24039533498978939,
    "gato_festejando": 1736736493414401,
    "okis": 268811655677102,
    "cachetada": 275511571531644,
    "gato_juzgando": 107235069063072,
    "chicorita": 3431648470417135,
    "gato_triste": 210492141865964,
    "gato_cansado": 1021308728970759
}

settings = Settings()