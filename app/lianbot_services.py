import httpx
import json
from core.config import settings as sett
from core.whatsapp_messaging import *
from asyncio import sleep
from database import DatabaseManager


async def guardar_datos_db(data):
    try:
        data = json.loads(data)
        
        if data["active"]:
            headers = {'Content-Type': 'application/json'}

            async with httpx.AsyncClient() as client:
                response = await client.post(f"{sett.API_WSP_MONGO}/v1/user/usuarios/", headers=headers, data=data)

            if response.status_code == 200:
                return 'MGS usuario guardado', 200
            else:
                print('error al guardar mensaje', response.status_code)
        else:
            print("El cliente esta desactivado")
            return False
        
    except Exception as e:
        return str(e), 403


async def enviar_Mensaje_whatsapp(data):
    try:
        # print(data)
        whatsapp_token = sett.wsp_token
        whatsapp_url = sett.wsp_url
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}

        async with httpx.AsyncClient() as client:
            response = await client.post(whatsapp_url, headers=headers, data=data)
            
        if response.status_code == 200:
            print('mensaje guardado', 200)
            return 'mensaje guardado', 200
        else:
            print("mensaje no enviado", response)
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return str(e), 403


async def obtener_Mensaje_whatsapp(message):
    if 'type' not in message:
        text = 'Mensaje no reconocido'
        return text

    typeMessage = message['type']

    if typeMessage == 'text':
        text = message['text']['body']
    elif typeMessage == 'button':
        text = message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        text = message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        text = message['interactive']['button_reply']['title']
    elif typeMessage == 'order':
        # Llama a una función que procesa y resume la orden, esta función se debe definir
        text = message['order']
        print(text)
    elif typeMessage == 'location':
        text = "Ubicación"
    elif typeMessage == 'image':
        text = message['image']
    else:
        text = 'mensaje no reconocido'

    return text


async def bloquear_usuario(text, number, messageId, name, timestamp, display_number=None):
    list_for = []

    async def Enviar_Saludo_Bloqueo():
        body = F"Disculpa🙏, parece que estoy un poco abrumado 🥱 por la cantidad de mensajes. Permíteme tomar un breve descanso de {sett.BLOCK_DURATION_SECONDS_TOKEN} segundos ⏳ para reorganizarme y estaré de vuelta contigo enseguida🏃💨. ¡Gracias por tu paciencia! 😊"
        data = await Enviar_MensajeIndividual_Message(number=number, messageId=messageId, text=body)
        return data
    if text:
        list_for.append(Enviar_Saludo_Bloqueo())

    return await enviar_mensaje_usuario(list_for)


async def enviar_mensaje_usuario(list_for):
    for item in list_for:
        await enviar_Mensaje_whatsapp(item)
        await sleep(1)


# Nuevo Forma
async def ObtenerTotalDeOrden_msg(number, data_orden, messageId):
    data = await Enviar_MensajeIndividual_Message(number, data_orden, messageId)
    return data


async def EnviarMetodosDePagos_img_options(number):
    body = "Aqui te envio los datos de transferencia"
    footer = "SF | Gracias por preferirnos ♥"
    options = ["Transferencia", "Pago en Efectivo", "3er Opcion"]
    # aca deberia consultar en la db, en la tabla proceso de pagos, columna imagen y hacer la consulta con la id o numero
    url_img = "https://i.postimg.cc/PJPRZJBh/e35f9d3b-f59b-44ed-91e2-e6742799baad.png"
    data = await ButtonImagenOpciones_Message(number, body=body, footer=footer, options=options, url_img=url_img)
    return data


async def Datos_para_descargarImagen(number, imagen_id, messageId):
    img_url = await ObtenerIdImagen(imagen_id)
    await descargar_imagen(img_url, number)
    data = await Enviar_MensajeIndividual_Message(number, "Gracias por el screeshot", messageId)
    return data


async def Send_Catalogo_wsp(number):
    try:
        body = "Te presento nuestro catalogo"
        footer = "SF | santiagofiltros.cl"
        idProductoCatalogo = "svtr266tw9"
        data = await Enviar_CatalgoSimpleWSP_Message(number, body, footer, idProductoCatalogo)
        return data
    except Exception as e:
        print(e)


async def RecibirUbicacion_Cliente(number):
    try:
        body = "Envianos tu dirección para ir a dejar tu pedido \n 👇"
        data = await Recibir_UbicacionCliente_Message(number, body)
        return data
    except Exception as e:
        print(e)


async def Enviar_Lista_Productos(number):
    try:
        lista_opciones = [
            {
                "title": "Filtro de aire 🍃",
                "rows": [
                    {
                        "id": "aire-identifier1",
                        "title": "F. Aire PDF",
                        # "description": "row-description-content"
                    },
                    {
                        "id": "aire-identifier2",
                        "title": "F. Aire WEb",
                        # "description": "row-description-content"
                    }
                ]
            },
            {
                "title": "Filtro de Combustible ⛽",
                "rows": [
                    {
                        "id": "combustible-identifier1",
                        "title": "F. Combustible PDF ",
                        # "description": "row-description-content"
                    },
                    {
                        "id": "combustible-identifier2",
                        "title": "F. Combustible WEb",
                        # "description": "row-description-content"
                    }
                ]
            },
            {
                "title": "Filtro de aceite 🏁",
                "rows": [
                    {
                        "id": "aceite-identifier1",
                        "title": "F. Aceite PDF",
                        # "description": "row-description-content"
                    },
                    {
                        "id": "aceite-identifier2",
                        "title": "F. Aceite Web",
                        # "description": "row-description-content"
                    }
                ]
            },

        ]
        body_text = "Productos de calidad, dale a tus cliente lo mejor"
        header_text = "Listado de Filtros"
        footer_text = "SF | Calidad y Confianza"
        button_text = "Ver ☑️"
        opciones = lista_opciones

        data = await Enviar_Lista_Opciones_Message(number, body_text, header_text, footer_text, button_text, opciones)
        return data
    except Exception as e:
        print(e)

#ok
async def Enviar_Flujo_Menu(number, flujo_menu, text, payload=None, messageId=None):
    # print("en flujo menu")
    # await guardar_datos_db(payload)
    if flujo_menu:
        # Construir el mensaje con los datos recuperados
        body = flujo_menu["flujo_menu"][text]["body"]
        footer = flujo_menu["flujo_menu"][text]["footer"]
        options = flujo_menu["flujo_menu"][text]["options"]
        sed = flujo_menu["flujo_menu"][text]["sed"]

        return await ButtonOpciones_Responder_msg(number, options, body, footer, sed)
    else:
        print("error en la db")

#ok
async def Descagar_pdf(number, flujo_pdf, text, payload=None, messageId=None):
    try:
        if flujo_pdf:
        # Construir el mensaje con los datos recuperados
            link = flujo_pdf["flujo_pdf"][text]["link"]
            caption = flujo_pdf["flujo_pdf"][text]["caption"]
            filename = flujo_pdf["flujo_pdf"][text]["filename"]

        data = await Enviar_Document_Message(number, link, caption, filename)
        return data
    except Exception as e:
        print(e)
        
#ok
async def Enviar_Lista_Servicios(number, flujo_list, text, payload=None, messageId=None):
    await guardar_datos_db(payload)
    if flujo_list:
        options = flujo_list['widget_list'][text]['options']
        body = flujo_list['widget_list'][text]['body']
        header = flujo_list['widget_list'][text]['header']
        footer = flujo_list['widget_list'][text]['footer']
        button = flujo_list['widget_list'][text]['button']

        data = await Enviar_Lista_Opciones_Message(number, body, header, footer, button, options)
        return data

#ok
async def Enviar_ButtonImagen(number, flujo, text, payload=None, messageId=None):
    await guardar_datos_db(payload)
    if flujo:
        body = flujo['flujo_submenu'][text]['body']
        footer = flujo['flujo_submenu'][text]['footer']
        options = flujo['flujo_submenu'][text]['options']
        link = flujo['flujo_submenu'][text]['link']
        options = flujo['flujo_submenu'][text]['options']
        data = await ButtonImagenOpciones_Message(number, body, footer, options, link)
        return data
    
#ok
async def Enviar_Ubicacion(number, flujo, text, playload=None, messageId=None):
    print(playload)
    if flujo:
        name = flujo['flujo_ubicacion'][text]['name']
        address = flujo['flujo_ubicacion'][text]['address']
        latitude = flujo['flujo_ubicacion'][text]['latitude']
        longitude = flujo['flujo_ubicacion'][text]['longitude']
        
    try:
        data = await Ubicacion_Empresa_Message(number, messageId, name, address, latitude, longitude)
        return data
    except Exception as e:
        print(e)


# deprecado
async def Enviar_Mensaje_ButtonImagen(number):
    body = "Te presento nuestras redes sociales, no olvides seguirnos para enterarte de ofertas y promociones del día"
    footer = "SF | Redes Sociales - FIX"
    options = ["Instagram", "Facebook", "TikTok"]
    url_img = "https://dinahosting.com/blog/upload/2022/07/tamanos-imagenes-redes-sociales-2024_dinahosting.png"
    data = await ButtonImagenOpciones_Message(number, body, footer, options, url_img)
    return data

async def Enviar_Menu_PrimerNegocio(number):
    body = "Tu primer negocio junto a SF | Confianza y Calidad"
    footer = "SF | Gracias por preferirnos ♥"
    options = ["Soy Cliente", "Primera Compra", "Ayuda PDF"]
    url_img = "https://i.postimg.cc/PJPRZJBh/e35f9d3b-f59b-44ed-91e2-e6742799baad.png"
    data = await ButtonImagenOpciones_Message(number, body, footer, options, url_img)
    return data


"""
Enviar contacto cuando lo solicitan, probar si podemos agregar varios contactos y podemos solicitar a cada uno
esto servira para los trainers 
"""
async def Mensaje_Contactar_Vendedor(number, flujo, text, playload=None, messageId=None):
    
    if flujo:
        vendedor = flujo['contacto_bot'][text]
        print(vendedor)
        return
        # data = await ButtonContact_Message(vendedor)
        # return data
        
async def Enviar_TienenPaginaWeb(number, flujo, text, payload, messageId):
    print("q fue")
    body = "Claro que si!, Visitanos en https://lianweb.cl para ayudarte en tu negocio, no dudes en llamarnos!"
    try:
        data = await Enviar_URLTexto_Message(number, body)
        return data
    except Exception as e:
        print(e)


async def Mensaje_Primera_Compra(number):

    lista_opciones = [
        {
            "title": "¿Cuál es tu presupuesto?",
            "rows": [
                {
                    "id": "presupuesto1",
                    "title": "CLP 100.000 - 300.000",
                    # "description": "row-description-content"
                },
                {
                    "id": "presupuesto2",
                    "title": "CLP 300.001 - 500.000",
                    # "description": "row-description-content"
                },
                {
                    "id": "presupuesto3",
                    "title": "CLP 500.001 - 700.000",
                    # "description": "row-description-content"
                },
                {
                    "id": "presupuesto4",
                    "title": "CLP 700.001 - XXX.XXX",
                    # "description": "row-description-content"
                }
            ]
        }
    ]
    header_text = "Presupuestos PREDETERMINADOS 🤟"
    body_text = "Selecciona el rango de compra 🛒 que mejor se ajusta a tus necesidades y te facilitaremos un PDF 📄 detallado para tu consulta. Este documento está diseñado con filtros específicos 🔍 para adaptarse a las particularidades de tu negocio 🏭, asegurando que encuentres exactamente lo que buscas de manera eficiente 💼."
    footer_text = "SF | Calidad y Confianza"
    button_text = "Ver Presupuestos 😎"
    opciones = lista_opciones
    data = await Enviar_Lista_Opciones_Message(number, body_text=body_text, header_text=header_text, footer_text=footer_text, button_text=button_text, opciones=opciones)
    return data


async def SinContext(number, messageId):
    body = "No tengo ese comando en mi sistema, dime como puedo ayudarte?"
    footer = "Equipo SF | santiagofiltros.cl"
    options = ["Catalogo", "Información", "Tu Negocio"]
    data = await ButtonOpciones_Responder_msg(number, options, body, footer, "sed7", messageId)
    return data


async def Enviar_Imagenes(number):
    link = "https://i.postimg.cc/4xzJdjY2/Personal-Portafolio.jpg"
    caption = "Enviamos esta imagen para su conocimiento"
    data = await Enviar_Imagen_MSG(number, link, caption)
    return data


async def Mensaje_Rapido(number, messageId, mensaje=None):
    return await Enviar_MensajeIndividual_Message(number, mensaje, messageId)


import unicodedata
async def administrar_chatbot(text, number, messageId, name, timestamp, display_number=None):
    list_for = []
    print(text)
    text = unicodedata.normalize("NFKD", text).encode("ascii","ignore").decode("ascii")
    text = text.lower().replace(" ", "_")
    db_manager = DatabaseManager()
    
    print("user:",text, "NumberHost: ", display_number)
    flujo = await db_manager.get_flujo_menu(display_number)

    # PODRIAMOS MEJORARLO CONSULTANDO A REDIS
    planes = { 
        "personal_cod:lp1":Enviar_ButtonImagen,
        "pyme_cod:lp2":Enviar_ButtonImagen,
        "pro_cod:lp3":Enviar_ButtonImagen,
        "personal_cod:pw1":Enviar_ButtonImagen,
        "Pyme cod:pw2":Enviar_ButtonImagen,
        "basico_cod:cb1":Enviar_ButtonImagen,
        "pro_cod:cb2":Enviar_ButtonImagen,
        "avanzado_cod:cb3":Enviar_ButtonImagen,
        "hola": Enviar_Flujo_Menu,
        "productos": Enviar_Flujo_Menu,
        "informacion": Enviar_Flujo_Menu,
        "pagina_web": Enviar_Lista_Servicios,
        "chat_bot": Enviar_Lista_Servicios,
        "ubicacion": Enviar_Ubicacion, 
        "landing_page": Enviar_Lista_Servicios,
        "pdf-lp1": Descagar_pdf, 
        "contacto_diego": Mensaje_Contactar_Vendedor, 
        "link_pagina_web": Enviar_TienenPaginaWeb
    }
    
    payload = json.dumps({
            "wsp_text": str(text),
            "wsp_name": name,
            "wsp_number": str(number),
            "wsp_wamid": messageId,
            "wsp_timestamp": str(timestamp),
            "wsp_display_phone_number": display_number,
            "active":flujo["active"]
        })
    # FLUJO DE MENUS
    if text in planes:
        list_for.append(await planes[text](number, flujo, text, payload, messageId))
        
    # INFORMACION
    elif "enviar ubicación" in text:
        list_for.append(await RecibirUbicacion_Cliente(number))
    elif "lista de productos" in text:
        list_for.append(await Enviar_Lista_Productos(number))
    # CREAR LOS ENLACES QUE LLEVEN AL USUARIO A BUSCAR LOS FILTROS www.santiagofitlros.cl/filtros/filtros-de-aire
    # Información

    elif text in "redes sociales":
        list_for.append(await Enviar_Mensaje_ButtonImagen(number))
    # OTROS MENSAJES
    elif text in "gracias":
        list_for.append(await Mensaje_Rapido(number, messageId, "Estamos para ayudarte 🤓", ))

    elif text in ["chao", "hasta luego"]:
        list_for.append(await Mensaje_Rapido(number, messageId, "Estamos para ayudarte 🤓", ))

    elif text in "ok":
        list_for.append(await Mensaje_Rapido(number, messageId, "😎"))
    else:
        list_for.append(await SinContext(number, messageId))

    return await enviar_mensaje_usuario(list_for)
