import os
import json
import httpx
from .config import settings as sett
from uuid import uuid4
import asyncio


#OBTENEMOS LA IMAGEN QUE NOS ENVIA EL USUARIO DESDE WHATSAPP
async def ObtenerIdImagen(image_id):
    url = f"{sett.FB_URL}/v19.0/{image_id}"
    whatsapp_token = sett.wsp_token
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {whatsapp_token}"}
        response = await client.get(url, headers=headers)
        data_json = response.json()
        imagen_url = data_json['url']
        return imagen_url

#SE DESCARGA LA IMAGEN QUE EL USUARIO ENVIA DESDE WHATSAPP, 
async def descargar_imagen(url, number):
    print(url)
    whatsapp_token = sett.wsp_token
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {whatsapp_token}"}
        # la url es la url que obtenemos del json de ObtenerIdImagen
        response = await client.get(url, headers=headers)
        # Guardar la imagen en un archivo local
        nombre_archivo = f"{number}_{uuid4()}.jpg"
        ruta_carpeta = os.path.join("imagenes")
        # Crear la carpeta si no existe
        os.makedirs(ruta_carpeta, exist_ok=True)
        # Guardar la imagen en la carpeta
        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
        with open(ruta_completa, "wb") as f:
            f.write(response.content)

#SUMAMOS EL TOTAL DEL PEDIDO QUE NOS HAGA EL CLIENTE
async def sumar_total_pedido(product_items):
    total = 0
    for item in product_items:
        total += item['item_price'] * item['quantity']
    return total

#PROCESAMOS LA ORDEN DE PEDIDO DEL USUARIO Y ENVIAMOS EL TOTAL
async def procesar_orden(order):
    total_pedido = await sumar_total_pedido(order['product_items'])
    return f'Orden recibida. Total del pedido: {total_pedido} {order["product_items"][0]["currency"]}'

#ENVIAMOS UNA IMAGEN DE NOSOTROS HACIA EL CLIENTE
async def Enviar_Imagen_MSG(number, link, caption):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "image",
        "image": {
            "link": link,
            "caption": caption
        }
    })
    return data

#Enviamos un mensaje que contiene texto, footer y opciones
async def ButtonOpciones_Responder_msg(number, options, body, footer, sed, messageId=None):
    buttons = []

    for i, option in enumerate(options):
        buttons.append({
            "type": "reply",
            "reply": {
                "id": sed + "_btn_" + str(i+1),
                "title": option
            }
        })
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "footer": {
                    "text": footer
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
    )
    return data

#enviamos una imagen con opciones
async def ButtonImagenOpciones_Message(number, body, footer, options, url_img):
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

#ENVIAMOS CONTACTO AL USUARIO DE WHATSAPP
async def ButtonContact_Message(number):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "contacts",
        "contacts": [
            {
                "addresses": [
                    {
                        "street": "Por redes sociales",
                        "city": "Iquique",
                        "state": "Alto Hospicio",
                        "country": "Chile",
                        "type": "HOME"
                    }
                ],
                "birthday": "1963-07-25",
                "emails": [
                    {
                        "email": "santiago@santiagofiltros.cl",
                        "type": "WORK"
                    }
                ],
                "name": {
                    "first_name": "Santiago",
                    "last_name": "Luque",
                    "formatted_name": "Santiago Luque"
                },
                "org": {
                    "company": "Santiago Filtros",
                    "department": "Ventas",
                    "title": "Vendedor"
                },
                "phones": [
                    {
                        "phone": "+56 98173 2415",
                        "wa_id": "56981732415",
                        "type": "WORK"  # "<HOME|WORK>"
                    }
                ],
                "urls": [
                    {
                        "url": "https://www.instagram.com/santiagofiltros/",
                        "type": "WORK"
                    }
                ]
            },
            # PARA ENVIAR OTRO CONTACTO
            {
                "addresses": [
                    {
                        "street": "Por redes sociales",
                        "city": "Iquique",
                        "state": "Alto Hospicio",
                        "country": "Chile",
                        "type": "HOME"
                    }
                ],
                "birthday": "1963-07-25",
                "emails": [
                    {
                        "email": "santiago@santiagofiltros.cl",
                        "type": "WORK"
                    }
                ],
                "name": {
                    "first_name": "Santiago",
                    "last_name": "Luque",
                    "formatted_name": "Santiago Luque"
                },
                "org": {
                    "company": "Santiago Filtros",
                    "department": "Ventas",
                    "title": "Vendedor"
                },
                "phones": [
                    {
                        "phone": "+56 98173 2415",
                        "wa_id": "56981732415",
                        "type": "WORK" #"<HOME|WORK>"
                    }
                ],
                "urls": [
                    {
                        "url": "https://www.instagram.com/santiagofiltros/",
                        "type": "HOME"
                    }
                ]
            }
        ]
    })
    return data

#ENVIAMOS UN TEXTO MAS UNA URL PARA QUE NOS VAYAN A VISITAR
async def Enviar_URLTexto_Message(number, body):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "text": {
            "preview_url": True,
            "body": body
        }
    })
    return data

#ENVIAMOS DOCUMENTO PDF WORD ETC A USUARIO WHATSAPP
async def Enviar_Document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {
                "link": url,
                "caption": caption,
                "filename": filename
            }
        }
    )
    return data


#ENVIAMOS NUESTRA UBICACION AL USUARIO
async def Ubicacion_Empresa_Message(number, messageId, name, address, latitude, longitude):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "context": {
            "message_id": messageId
        },
        "type": "location",
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "name": name,
            "address": address
        },
    })
    return data

#ENVIAMOS UN MENSAJE INTERACTIVO DE HEADER, BODY FOOTER Y OPCIONES
async def Enviar_Lista_Opciones_Message(number, body, header, footer, button, options):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": header
            },
            "body": {
                "text": body
            },
            "footer": {
                "text": footer
            },
            "action": {
                "button": button,
                "sections": options

            }
        }
    })
    return data

#EL USUARIO NOS ENVIA SU UBICACION 
async def Recibir_UbicacionCliente_Message(number, body):

    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "to": number,
        "interactive": {
            "type": "location_request_message",
            "body": {
                "text": body
            },
            "action": {
                "name": "send_location"
            }
        }
    })

    return data

#Enviamos el catalogo de nuestros productos de Facebook
async def Enviar_CatalogoWSP_Message(number, body, idProductoCatalogo, footer):
    number = "56961227637"
    body = "Descubre nuestra gama de filtros para vehículos 🚗: calidad y rendimiento para mantener tu motor en óptimas condiciones. ¡Echa un vistazo ahora!"
    idProductoCatalogo = "svtr266tw9"
    footer = "Best grocery deals on WhatsApp!"
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "catalog_message",
            "body": {
                "text": body
            },
            "action": {
                "name": "catalog_message",
                "parameters": {
                    "thumbnail_product_retailer_id": idProductoCatalogo
                }
            },
            "footer": {
                "text": footer
            }
        }
    })
    return data

#ENVIAMOS EL CATALOGO SIMPLE POR WHATSAPP 
async def Enviar_CatalgoSimpleWSP_Message(number, body, footer, idProductoCatalogo):
    
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "catalog_message",
                "body": {
                    "text": body
                },
                "action": {
                    "name": "catalog_message",
                    "parameters": {
                        "thumbnail_product_retailer_id": idProductoCatalogo
                    }
                },
                "footer": {
                    "text": footer
                }
            }
        }
    )
    return data

#SI QUEREMOS ENVIAR VARIOS MENSAJES EN DISTINTOS BLOQUES
async def Enviar_VariosMensajes_Message(numero, messageId):
    mensajes = ["¡Estamos encantados de darte la bienvenida a nuestra comunidad de clientes! Es un placer tenerte con nosotros en tu primera compra. 😊","Queremos que sepas que ofrecemos una diversidad de opciones para asegurarnos de que encuentres exactamente lo que necesitas, adaptándonos a todo tipo de presupuestos. Ya sea que busques algo económico o estés buscando invertir en productos de calidad, tenemos lo justo para ti."
                        ]
    tasks = [await Enviar_MensajeIndividual_Message(numero, mensaje, messageId) for mensaje in mensajes]
    return tasks

#ENVIAMOS MENSAJES BASICOS(INDIVIDUAL)
async def Enviar_MensajeIndividual_Message(number, text, messageId=None):
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

#enviamos stickers
async def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {
                "id": sticker_id
            }
        }
    )
    return data
    # {'object': 'whatsapp_business_account', 'entry': [{'id': '131989103328203',
    # 'changes': [{'value': {'messaging_product': 'whatsapp',
    # 'metadata': {'display_phone_number': '56934888609', 'phone_number_id': '130513470143872'},
    # 'contacts': [{'profile': {'name': 'JD'}, 'wa_id': '56961227637'}],
    # 'messages': [{'from': '56961227637', 'id': 'wamid.HBgLNTY5NjEyMjc2MzcVAgASGBQzQTU1QTc1REZCMkM0RTlGREE5NAA=',
    # 'timestamp': '1711930371', 'type': 'sticker',
    # 'sticker': {'mime_type': 'image/webp',
    # 'sha256': 'uwXVoi2i4wLtzkMQAP7ySI3p7MNqzU+PM/RWn1GBwO0=',
    # 'id': '381731608015965',
    # 'animated': False}
    # }]}, 'field': 'messages'}]}]}


async def get_media_id(media_name, media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    # elif media_type == "image":
    #    media_id = sett.images.get(media_name, None)
    # elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    # elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id


#ENVIAMOS UN MENU, BODY, FOOTER Y OPCIONES CON UN MAXIMO DE 3 ITEMS
async def Enviar_Menu_Message(number, messageId, body, footer, options, sed):
    replyButton_Data = await ButtonOpciones_Responder_msg(number, options, body, footer, sed=sed, messageId=messageId)
    return replyButton_Data


#marcamos los mensaje del usuario como leido
async def markRead_Message(messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id":  messageId
        }
    )
    return data
