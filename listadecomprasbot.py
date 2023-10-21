import telebot, logging, time
from telebot.types import ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
#from flask import Flask, request # Solo es necesario en WebHook
#from waitress import serve # Solo es necesario en WebHook
#from pyngrok import ngrok, conf # Solo es necesario en WebHook
from config import TELEGRAM_TOKEN, ADMIN_USER_ID#, NGROK_TOKEN
from db.models import session, User, Item

# Configuración de logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs.txt")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(stream_handler)

# Configuración del bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Solo es necesario en WebHook
"""web_server = Flask(__name__)
@web_server.route('/', methods=['POST'])
def server():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode('uft-8'))
        bot.process_new_updates([update])
        return "Ok", 200"""

COMMANDS_MENU = """Mi función es recordar tu lista de compras, puedes probar los siguientes comandos:
<b>/iniciar:</b> Te muestro este menú
<b>/cambiar_nombre:</b> Te llamo de otra forma
<b>/cambiar_nombre [nombre]:</b> Te llamo de otra forma
<b>/comprar:</b> Te pregunto que necesitas comprar y lo guardaré
<b>/comprar [objeto]:</b> Guardaré el objeto que escribas
<b>/lista:</b> Te muestro la lista de las cosas que necesitas comprar
<b>/borrar:</b>, Te pregunto que objeto de la lista quieres borrar
<b>/borrar [número]:</b>, Borraré el objeto que indiques
<b>/borrar_todo:</b>, Borraré todos los objetos en tu lista
"""

# Stickers
STICKER_HI = "CAACAgIAAxkBAAEm9H9lMMRGk8yENzDcgKyGKMa7zK6XwgACyQADmL-ADZ3o05MJ4JudMAQ"
STICKER_OK = "CAACAgIAAxkBAAEm9ThlMO1k6BrG9ESVxl9FVvt7rXoukAACxwADmL-ADQo8flQAAaM1VDAE"
STICKER_LIST = "CAACAgIAAxkBAAEm9VRlMPGIKjGDBkpJ_sk_SOz0WZOmIgACyAADmL-ADcamQJREKQw9MAQ"
STICKER_ADD_LIST = "CAACAgIAAxkBAAEm9WJlMPMIgp1Rpx7ncQmb9rF11aBzngACzQADmL-ADVM3MFEaM0aZMAQ"
STICKER_EMPTY_LIST = "CAACAgIAAxkBAAEm9VxlMPIkbrqYz6s2-Hrb78yg0xSZAAPUAAOYv4ANhOC6EWjNGAswBA"
STICKER_DELETED_LIST = "CAACAgIAAxkBAAEm_8hlM3lHiDICn5up0jIF2o8eCi0CYgACywADmL-ADRzqSfeVAAEokjAE"
STICKER_COMMAND_NOT_FOUND = "CAACAgIAAxkBAAEm_75lM3V_WLWh-QJwEU7Lhj-xoDXGWgACygADmL-ADTl5jp4TkeZ0MAQ"

# Funciones del bot
# iniciar
@bot.message_handler(commands=['start', 'help', 'iniciar', 'ayuda'])
def start(message):
    logger.info(f'El usuario "{message.from_user.first_name}" ({message.from_user.username}) inició el bot')
    user = session.query(User).filter_by(id=message.from_user.id).first()
    bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_HI)
    if user:
        bot.send_message(chat_id=message.chat.id, text=f'Hola <b>{user.name}</b>\n{COMMANDS_MENU}', parse_mode="HTML")
    else:
        msg = bot.send_message(chat_id=message.chat.id, text=f'Hola {message.from_user.username}, eres un usuario nuevo. \n¿Como quieres que te llame?', reply_markup=ForceReply())
        bot.register_next_step_handler(msg, login)

def login(message):
    user = User(id=message.from_user.id, name=message.text, username=message.from_user.username)
    session.add(user)
    session.commit()
    bot.send_message(chat_id=message.chat.id, text=f'Excelente, te llamaré <b>{user.name}</b>.', parse_mode="HTML")
    logger.info(f'El usuario "{message.from_user.first_name}" ({message.from_user.username}) se registró como {user.name}')
    bot.send_message(chat_id=message.chat.id, text=f'Hola <b>{user.name}</b>\n{COMMANDS_MENU}', parse_mode="HTML")

# Cambiar el nombre del usuario
@bot.message_handler(commands=['cambiar_nombre'])
def ask_new_name(message):
    if message.text[15:]:
        change_name(message)
    else:
        msg = bot.send_message(chat_id=message.chat.id, text=f'No hay problema, ¿como quieres que te llame ahora?', reply_markup=ForceReply())
        bot.register_next_step_handler(msg, change_name)
    
def change_name(message):
    name = message.text.replace("/cambiar_nombre ", "")
    session.query(User).filter(User.id == message.from_user.id).update({User.name: name})
    session.commit()
    logger.info(f'El usuario "{message.from_user.first_name}" ({message.from_user.username}) se cambió el nombre a {name}')
    bot.send_message(chat_id=message.chat.id, text=f'Excelente, ahora te llamaré <b>{name}</b>.', parse_mode="HTML")

# Añadir un item a la lista del usuario
@bot.message_handler(commands=['comprar'])
def ask_item_name(message):
    if message.text[9:]:
        save_item(message)
    else:
        msg = bot.send_message(chat_id=message.chat.id, text=f'¿Que necesitas comprar?', reply_markup=ForceReply())
        bot.register_next_step_handler(msg, save_item)

def save_item(message):
    item = Item(user_id=message.from_user.id, name=message.text.replace("/comprar ", ""))
    session.add(item)
    session.commit()
    bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_ADD_LIST)
    bot.send_message(chat_id=message.chat.id, text=f'Excelente, he añadido <b>{item.name}</b> a tu lista.', parse_mode="HTML")

# Mostrar la lista de productos al usuario
@bot.message_handler(commands=['lista'])
def list(message):
    bot.send_chat_action(message.chat.id, "typing")
    items = session.query(Item).filter(Item.user_id == message.from_user.id).all()
    name = session.query(User.name).filter(User.id == message.from_user.id).scalar()
    if items:
        bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_LIST)
        list = f"<b>{name}</b>, tu lista de compras es:"
        n = 1
        for item in items:
            list+= f"\n<b>{n})</b>\t{item.name}"
            n += 1
        
        bot.send_message(chat_id=message.chat.id, text=list, parse_mode="HTML")
    else:
        bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_EMPTY_LIST)
        bot.send_message(chat_id=message.chat.id, text=f'<b>{name}</b>, no he encontrado objetos en tu lista', parse_mode="HTML")

# Borrar algún objeto de la lista
@bot.message_handler(commands=['borrar'])
def ask_item(message):
    items = session.query(Item).filter(Item.user_id == message.from_user.id).all()
    name = session.query(User.name).filter(User.id == message.from_user.id).scalar()
    if not items:
        bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_EMPTY_LIST)
        bot.send_message(chat_id=message.chat.id, text=f'<b>{name}</b>, no he encontrado objetos en tu lista')
    elif message.text[8:]:
        delete_item(message)
    else:
        list = f"<b>{name}</b>, tu lista de compras es:"
        n = 1
        for item in items:
            list+= f"\n<b>{n})</b>\t{item.name}"
            n += 1
        
        bot.send_message(chat_id=message.chat.id, text=list, parse_mode="HTML")
        msg = bot.send_message(chat_id=message.chat.id, text='Escribe el número del objeto a borrar', reply_markup=ForceReply())
        bot.register_next_step_handler(msg, delete_item)

def delete_item(message):
    number = message.text.replace("/borrar ", "")
    try:
        n = int(number)-1
        items = session.query(Item).filter(Item.user_id == message.from_user.id).all()
        session.query(Item).filter(Item.id == items[n].id).delete()
        session.commit()
        bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_OK)
        bot.send_message(chat_id=message.chat.id, text=f'Se borró el objeto <b>{items[n].name}</b> correctamente', parse_mode="HTML")
    except:
        bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_COMMAND_NOT_FOUND)
        msg = bot.send_message(chat_id=message.chat.id, text=f'El valor <b>{number}</b> no es válido, ingresa un número correcto', reply_markup=ForceReply(), parse_mode="HTML")
        bot.register_next_step_handler(msg, delete_item)

# Borrar todos los objetos en la lista del usuario
@bot.message_handler(commands=['borrar_todo'])
def delete_list(message):
    items = session.query(Item).filter(Item.user_id == message.from_user.id).all()
    name = session.query(User.name).filter(User.id == message.from_user.id).scalar()
    if not items:
        bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_EMPTY_LIST)
        bot.send_message(chat_id=message.chat.id, text=f'<b>{name}</b>, no he encontrado objetos en tu lista', parse_mode="HTML")
    else:
        markup = InlineKeyboardMarkup(row_width=2)
        button_yes = InlineKeyboardButton("Si", callback_data="borrar_lista")
        button_no = InlineKeyboardButton("No", callback_data="no_borrar_lista")
        markup.add(button_yes, button_no)
        bot.send_message(chat_id=message.chat.id, text='¿Seguro quieres borrar tu lista?', reply_markup=markup)
        
@bot.callback_query_handler(func=lambda x:True)
def confirm_delete(call):
    cid = call.from_user.id
    mid = call.message.id
    if call.data == "borrar_lista":
        bot.delete_message(cid, mid)
        session.query(Item).filter(Item.user_id == cid).delete()
        session.commit()
        bot.send_sticker(chat_id=cid, sticker=STICKER_DELETED_LIST)
        bot.send_message(chat_id=cid, text='Todos los objetos en tu lista han sido eliminados')
    elif call.data == "no_borrar_lista":
        bot.delete_message(cid, mid)
        bot.send_sticker(chat_id=cid, sticker=STICKER_OK)
        bot.send_message(chat_id=cid, text='Ok, no borraré tu lista')
    else:
        pass


# Enviar el log al administrador
@bot.message_handler(commands=['log', 'logs'])
def send_log(message):
    if message.from_user.id == ADMIN_USER_ID:
        with open("logs.txt", "rb") as file:
            bot.send_document(chat_id=message.chat.id, document=file)
    else:
        bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_COMMAND_NOT_FOUND)
        bot.send_message(chat_id=message.chat.id, text=f'No conozco el comando <b>{message.text}</b>', parse_mode="HTML")

# Al recibir cualquier otro mensaje/comando
@bot.message_handler()
def default_handler(message):
    bot.send_sticker(chat_id=message.chat.id, sticker=STICKER_COMMAND_NOT_FOUND)
    bot.send_message(chat_id=message.chat.id, text=f'No conozco el comando <b>{message.text}</b>', parse_mode="HTML")


if __name__ == '__main__':
    try:
        bot.set_my_commands([
            telebot.types.BotCommand("/iniciar", "Inicia el bot y explica los comandos"),
            telebot.types.BotCommand("/cambiar_nombre", "Cambia el nombre del usuario"),
            telebot.types.BotCommand("/comprar", "Añade un objeto a la lista"),
            telebot.types.BotCommand("/lista", "Muestra la lista de objetos"),
            telebot.types.BotCommand("/borrar", "Borra un item de la lista"),
            telebot.types.BotCommand("/borrar_todo", "Borra todos los objetos en tu lista"),
        ])
        logger.info('El bot está encendido')
        bot.remove_webhook() # Solo necesario para volver a infinity_polling()
        time.sleep(1) # Solo necesario para volver a infinity_polling()
        bot.infinity_polling()

        """# Solo es necesario en WebHook
        conf.get_default().config_path = './config_ngrok.yml'
        conf.get_default().region = 'sa'
        ngrok.set_auth_token(NGROK_TOKEN)
        ngrok_tunnel = ngrok.connect(5000, bind_tls=True)
        ngrol_url = ngrok_tunnel.public_url
        logger.info(f'El bot se ha conectado a NGROK con la URL {ngrol_url}')
        time.sleep(1)
        bot.set_webhook(url=ngrol_url)
        web_server.run(host='0.0.0.0', port=5000)
        #serve(web_server, host='0.0.0.0', port=5000)"""

        logger.info('El bot está apagado')
    except Exception as e:
        logger.error(f'Ha ocurrido un error: {e}')
