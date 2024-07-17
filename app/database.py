from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis  # or from memcached.client import Client
import json
from core.config import settings as sett

class DatabaseManager:
    def __init__(self):
        self.databases = [
            {"type": "mongodb", "connection_str": sett.DB_MONGO_COMPAS},
            {'type': 'dynamodb', 'connection_str': {'region_name': 'us-east-1', 'aws_access_key_id': 'YOUR_ACCESS_KEY_ID', 'aws_secret_access_key': 'YOUR_SECRET_ACCESS_KEY'}}
        ]
        self.mongo_instance = None
        self.cache = Redis(host=sett.DB_REDIS if sett.DB_REDIS else "localhost", port=sett.DB_REDIS_PORT, db=0)  # Cache for storing chatbot flow menus

    async def connect(self, db_type):
        db = next((db for db in self.databases if db['type'] == db_type), None)

        if db is None:
            print(f"No database of type {db_type} found")
            return None

        if db_type == 'mongodb':
            print("db_conectado")
            self.mongo_instance = AsyncIOMotorClient(db['connection_str'])
            return self.mongo_instance["lianbot_db"]

    async def disconnect(self, db_type):
        print("disconnect")
        if db_type == 'mongodb':
            if self.mongo_instance:
                await self.mongo_instance.close()

    async def get_flujo_menu(self, display_number=None):
        #numero del chatbot
        number = "56934888609"
        print("get_flujo_display: ", display_number)
        """
        SOLUCIONAR PROBLEMA CON REDIS DE LOCAL Y NUBE
        """
        if valor_in_cache:=self.cache.get(number):
            # Si el valor existe en caché, decodificarlo de bytes a dict
            flujo_menu = json.loads(valor_in_cache.decode())
            print("Flujo de menú encontrado en caché")
            return flujo_menu
        else:
            # Si el valor no está en caché, recuperarlo de la base de datos y guardarlo en caché
            conn = await self.connect('mongodb')
            flujo_menu = await conn['menu_col'].find_one({"numero_celular": number})

            if flujo_menu:
                # Almacenar el valor en Redis antes de devolverlo
                self.cache.set(number, json.dumps(flujo_menu))
                duration = int(sett.DURATION_REDIS_FLUJO if sett.DURATION_REDIS_FLUJO else 3600)
                self.cache.expire(number, duration)
                print("Flujo de menú recuperado de la base de datos y guardado en caché")
                return flujo_menu
            else:
                print("Flujo de menú no encontrado en la base de datos o caché")
                return None