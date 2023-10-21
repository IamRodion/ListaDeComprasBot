# ListaDeComprasBot

Este programa es un bot de Telegram que gestiona lista de compras de diferentes usuarios a través del bot 
[Lista de Compras](https://t.me/MiListaDeComprasBot) en Telegram.

## Características
Para crear tu propio bot con este proyecto debes tener en cuenta lo siguiente:

* Necesitas crear un bot de Telegram, obtener su token y almacenarlo en `config.py`:
* Necesitas indicar tu chat ID de Telegram en `config.py`.
* Sí usarás web hook en vez de infinitypolling debes crear un usuario de Ngrok y guardar el token en `config.py`.

### El archivo `config.py` debe quedar algo así:
```Python
TELEGRAM_TOKEN = "EL_TOKEN_DEL_BOT"
NGROK_TOKEN = "EL_TOKEN_DEL_NGROK"
ADMIN_USER_ID = 1234567890
```

## Instalación
Para instalar este proyecto, sigue estos pasos:
```Bash
git clone https://github.com/IamRodion/ListaDeComprasBot.git
```
```Bash
cd ListaDeComprasBot/
```
```Bash
pip3 install -r requirements.txt
```
```Bash
python3 listadecomprasbot.py
```

## Uso
Para usar este bot, sigue estos pasos:

1. Abre telegram y busca @MiListaDeComprasBot o da click [aquí](https://t.me/MiListaDeComprasBot).
2. Pulsa el botón `INICIAR` o escribe `/iniciar`.
3. El bot te preguntará un nombre para registrarte y guardar tu lista (puedes cambiarlo luego).

### Comandos del bot

+ `/iniciar` -> Iniciar el bot
+ `/cambiar_nombre [nombre]` -> Cambiar el nombre de usuario
+ `/comprar [objeto]` -> Añadir un objeto a la lista de compras
+ `/lista` -> Mostrar la lista de compras
+ `/borrar [número]` -> Borrar un objeto de la lista de compras
+ `/borrar_todo` -> Borrar toda la lista de compras


## Requisitos
Este proyecto requiere los siguientes requisitos:

* Python 3.10.6 o superior.
* Las librerías en requirements.txt
* Un Bot de Telegram.

## Problemas conocidos

* No se ha probado en sistemas operativos diferentes de Linux.

## Contacto
Si tienes alguna pregunta o problema, contacta con [Rodion](github.com/IamRodion)