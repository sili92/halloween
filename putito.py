import datetime
import random
import re
import os
import pytz
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_USERNAME = 'kirschteiinz'  # Sin el '@'

# ID numéricos exactos de tus grupos de Telegram
GROUPS = {'cherrys': -1002327728583, 'testing': -1004332628770}

# Base de datos interna unificada
db = {
    'users': {},  # { username: {'caramelos': 0, 'bannedUntil': None, 'user_id': id, ...} }
    'activeHunt': {'active': False, 'targetGroup': None},
    'activeWitch': None,
    'graves_today': [0, 0, 0, 0, 0],
}

# Diccionario temporal para guardar el inventario y efectos de los usuarios
inventario = {}  # { user_id: {'pocion_venenosa': 0, 'escudo_activo': True/False, 'veneno_until': datetime, ...} }

# Símbolos para la tragamonedas de Halloween
SLOT_SYMBOLS = ["🎃", "👻", "🦇", "💀", "🍬", "🕷️", "🩸", "🧛"]

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# === DICCIONARIO DE TIPOS DE BRUJAS ===
# ==========================================
WITCH_TYPES = {
    'comun': {
        'name': 'común',
        'reward': 20,
        'photo': 'https://pin.it/5cBvTP7zt',
        'caption': (
            '   ⬚   ㅤㅤ     ¡𝗁𝖺𝗒 𝗎𝗇𝖺 𝖻𝗋𝗎𝗃𝖺 v𝗈𝗅𝖺𝗇𝖽𝗈 𝘱𝗈𝗋 𝖾𝗅'
            ' 𝖼𝗂𝖾𝗅𝗈!\nㅤㅤㅤ ㅤ  𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝘱𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎'
            ' 𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 20 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁𝖾c𝗁𝗈!'
        ),
    },
    'bosque': {
        'name': 'bosque',
        'reward': 50,
        'photo': 'https://pin.it/51WPNtD0s',
        'caption': (
            '   ⬚   ㅤㅤ     ¡𝖾𝗇𝖼𝗈𝗇𝗍𝗋𝖺𝗌𝗍𝖾 𝗎𝗇𝖺 𝖻𝗋𝗎𝗃𝖺 𝖾𝗇 𝖾𝗅'
            ' 𝖻𝗈𝗌𝗊𝗎𝖾!\nㅤㅤㅤ ㅤㅤ 𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎'
            ' 𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 50 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁𝖾c𝗁𝗈!'
        ),
    },
    'noche': {
        'name': 'noche',
        'reward': 80,
        'photo': 'https://pin.it/4mD78Eta5',
        'caption': (
            '   ⬚   ㅤㅤ     ¡𝗎𝗇𝖺 𝖻𝗋𝗎𝗃𝖺 𝗇𝗈𝖼𝗍𝗎𝗋𝗇𝖺 𝗁𝖺'
            ' 𝖾𝗆𝖾𝗋𝗀𝗂𝖽𝗈!\nㅤㅤㅤ ㅤ  𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎'
            ' 𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 80 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁ec𝗁𝗈!'
        ),
    },
    'piromantica': {
        'name': 'piromantica',
        'reward': 100,
        'photo': 'https://pin.it/KobOJHTjv',
        'caption': (
            '   ⬚   ㅤ    ¡𝗐𝗈𝗐! 𝗁𝖺 𝖺𝗉𝖺𝗋𝖾𝖼𝗂𝖽𝗈 𝗎𝗇𝖺 𝖻𝗋𝗎𝗃𝖺'
            ' 𝗉𝗂𝗋𝗈𝗆𝖺𝗇𝗍𝗂𝖼𝖺 \nㅤㅤ    𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎'
            ' 𝖿𝗅𝖺𝗆𝖺𝗇𝗍𝖾  𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 100 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁𝖾𝖼𝗁𝗈!'
        ),
    },
    'nigromante': {
        'name': 'nigromante',
        'reward': 150,
        'photo': 'https://pin.it/1cCDYz0dy',
        'caption': (
            '   ⬚   ㅤ    ¡𝗎𝗇𝖺 𝖻𝗋𝗎𝗃𝖺 𝗇𝗂𝗀𝗋𝗈𝗆𝖺𝗇𝗍𝖾 𝗁𝖺 𝗌𝖺𝗅𝗂𝖽𝗈 𝖽𝖾 𝗌𝗎'
            ' 𝗍𝗎𝗆𝖻𝖺!\nㅤㅤ    𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎 𝗌𝗈𝗆𝖻𝗋í𝗈'
            ' 𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 150 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁𝖾𝖼𝗁𝗈!'
        ),
    },
    'reina': {
        'name': 'reina',
        'reward': 200,
        'photo': 'https://pin.it/40Xd932NM',
        'caption': (
            '   ⬚   ㅤ    ¡𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝗋𝖾𝗂𝗇𝖺 𝖾𝗌𝗍á 𝗋𝖾𝗉𝖺𝗋𝗍𝗂𝖾𝗇𝖽𝗈 𝗌𝗎'
            ' 𝖿𝗈𝗋𝗍𝗎𝗇𝖺! \nㅤㅤ    𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎 𝗍𝖾𝗇𝗍𝖺𝖽𝗈𝗋'
            ' 𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 200 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁𝖾𝖼𝗁𝗈!'
        ),
    },
    'mitica': {
        'name': 'mítica',
        'reward': 400,
        'photo': 'https://pin.it/5tH8YxmBX',
        'caption': (
            '   ⬚   ㅤ    ¡𝗎𝗇𝖺 𝖻𝗋𝗎𝗃𝖺 𝗆í𝗍𝗂𝖼𝖺 𝗏𝗎𝖾𝗅𝖺 𝗌𝗈𝖻𝗋𝖾 𝗌𝗎'
            ' 𝖾𝗌𝖼𝗈𝖻𝖺! \nㅤㅤ    𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎 𝖻𝗋𝗂𝗅𝗅𝖺𝗇𝗍𝖾'
            '  𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 400 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁𝖾𝖼𝗁𝗈!'
        ),
    },
    'madre': {
        'name': 'madre',
        'reward': 600,
        'photo': 'https://pin.it/Jjr04T2Wk',
        'caption': (
            '   ⬚   ㅤ    ¡𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝗆𝖺𝖽𝗋𝖾 𝗅𝗅𝖾𝗏𝖺 𝗎𝗇𝖺 𝖀𝗋𝖺𝗇 𝖿𝗈𝗋𝗍𝗎𝗇𝖺'
            ' 𝖼𝗈𝗇 𝖾𝗅𝗅𝖺! \nㅤㅤ     𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎 𝘱𝗋𝖾𝖼𝗂𝗈𝗌𝗈'
            ' 𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 600 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝖻𝗂𝖾𝗇 𝗁𝖾𝖼𝗁𝗈!'
        ),
    },
    'suprema': {
        'name': 'suprema',
        'reward': 1000,
        'photo': 'https://pin.it/7Lw3n7KwR',
        'caption': (
            '   ⬚   ㅤ    ¡𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝗌𝗎𝗉𝗋𝖾𝗆𝖺 𝗌𝖾 𝗏𝖾 𝖼𝖺𝗋𝗀𝖺𝖽𝖺 𝖽𝖾'
            ' 𝘱𝗋𝖾𝗆𝗂𝗈𝗌! \nㅤㅤ     𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺 𝗉𝖺𝗋𝖺 𝗊𝗎𝖾𝖽𝖺𝗋𝗍𝖾 𝖼𝗈𝗇 𝗌𝗎 𝘱𝗋𝖾𝖼𝗂𝗈𝗌𝗈'
            ' 𝗍𝖾𝗌𝗈𝗋𝗈.ㅤㅤ ،͟،'
        ),
        'caughtCaption': lambda user: (
            f'ㅤㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋 @{user}\nㅤㅤㅤ𝗒'
            ' 𝗈𝖻𝗍𝗎𝗏𝗈 1000 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. ¡𝗌𝗈𝗋𝗉𝗋𝖾𝗇𝖽𝖾𝗇𝗍𝖾!'
        ),
    },
    'misteriosa': {
        'name': 'misteriosa',
        'reward': 0,
        'photo': 'https://pin.it/7gR6Dfu93',
        'caption': (
            '   ⬚   ㅤ    𝖾𝗌𝗍𝖺 𝖻𝗋𝗎𝗃𝖺 𝗈𝖿𝗋𝖾𝖼𝖾 𝗎𝗇𝖺 𝖽𝗎𝖽𝗈𝗌𝖺'
            ' 𝗋𝖾𝖼𝗈𝗆𝗉𝖾𝗇𝗌𝖺...\nㅤㅤ     𝗉𝗎𝖾𝖽𝖾𝗌 𝖺𝗍𝗋𝖺𝗉𝖺𝗅𝖺𝗋𝗅𝖺, 𝗍𝖾𝗇'
            ' 𝖼𝗎𝗂𝖽𝖺𝖽𝗈...          ،͟،'
        ),
        'caughtCaption': lambda user, amount: (
            (
                f'ㅤㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋'
                f' @{user}\nㅤㅤㅤ𝗒 𝗈𝖻𝗍𝗎𝗏𝗈 {amount} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
                ' ¡𝗌𝗈𝗋𝗉𝗋𝖾𝗇𝖽𝖾𝗇𝗍𝖾!'
            )
            if amount >= 0
            else (
                f'ㅤㅤ ￤ ꜥꜤ ㅤㅤ𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝖿𝗎𝖾 𝖼𝖺𝗓𝖺𝖽𝖺 𝗉𝗈𝗋'
                f' @{user}\nㅤㅤㅤ𝖾𝗅𝗅𝖺 𝗅𝖾 𝗋𝗈𝖻ó {abs(amount)} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
                ' 𝗌𝖾 𝖿𝗎𝖾 𝖻𝗎𝗋𝗅𝖺𝗇𝖽𝗈𝗌𝖾.'
            )
        ),
    },
}

# ==========================================
# === FUNCIONES DE UTILIDAD ===
# ==========================================

def sanitize_username(username):
  if not username:
    return None
  return username.replace('@', '').strip()


def init_user(username, user_id=None):
  clean_user = sanitize_username(username)
  if not clean_user:
    return
  if clean_user not in db['users']:
    db['users'][clean_user] = {
        'caramelos': 100,
        'bannedUntil': None,
        'attempts': 5,
        'coraline_attempts': 5,
        'user_id': user_id,
    }
  elif user_id and not db['users'][clean_user].get('user_id'):
    db['users'][clean_user]['user_id'] = user_id


def is_banned(username):
  clean_user = sanitize_username(username)
  if not clean_user or clean_user not in db['users']:
    return False
  ban_time = db['users'][clean_user].get('bannedUntil')
  if not ban_time:
    return False
  now_tz = (
      datetime.datetime.now(ban_time.tzinfo)
      if ban_time.tzinfo
      else datetime.datetime.now()
  )
  if now_tz < ban_time:
    return True
  db['users'][clean_user]['bannedUntil'] = None
  return False


def check_poisoned(user_id):
  if user_id not in inventario:
    return False
  veneno_until = inventario[user_id].get("veneno_until")
  if not veneno_until:
    return False
  if datetime.datetime.now() < veneno_until:
    return True
  inventario[user_id]["veneno_until"] = None
  return False


def parse_duration(time_str):
  match = re.match(r'^(\d+)([hms])$', time_str, re.IGNORECASE)
  if not match:
    return None
  value = int(match.group(1))
  unit = match.group(2).lower()
  if unit == 'h':
    return datetime.timedelta(hours=value)
  elif unit == 'm':
    return datetime.timedelta(minutes=value)
  elif unit == 's':
    return datetime.timedelta(seconds=value)
  return None


def check_admin(message):
  user = message.from_user.username
  if user and user.lower() == ADMIN_USERNAME.lower():
    return True
  bot.reply_to(
      message,
      'ㅤ⬚  lo siento, solo la admin suprema @kirschteiinz puede usar esto.'
      '  ،͟,',
  )
  return False


def get_today_str_ve():
  tz_ve = pytz.timezone('America/Caracas')
  return datetime.datetime.now(tz_ve).strftime('%Y-%m-%d')


def init_game_users(username, user_id=None):
  init_user(username, user_id)
  clean_user = sanitize_username(username)
  today = get_today_str_ve()

  if 'graves_date' not in db['users'][clean_user]:
    db['users'][clean_user]['graves_date'] = today
    db['users'][clean_user]['graves_attempts'] = 0
  elif db['users'][clean_user]['graves_date'] != today:
    db['users'][clean_user]['graves_date'] = today
    db['users'][clean_user]['graves_attempts'] = 0

  if 'penny_date' not in db['users'][clean_user]:
    db['users'][clean_user]['penny_date'] = today
    db['users'][clean_user]['penny_attempts'] = 0
    db['users'][clean_user]['penny_extra'] = 0
    db['users'][clean_user]['penny_active'] = None
  elif db['users'][clean_user]['penny_date'] != today:
    db['users'][clean_user]['penny_date'] = today
    db['users'][clean_user]['penny_attempts'] = 0
    db['users'][clean_user]['penny_active'] = None


def init_bg_user(username, user_id=None):
  init_user(username, user_id)
  clean_user = sanitize_username(username)
  if 'bg_date' not in db['users'][clean_user]:
    db['users'][clean_user]['bg_date'] = get_today_str_ve()
    db['users'][clean_user]['bg_attempts'] = 0
    db['users'][clean_user]['extra_chances'] = 0
  if db['users'][clean_user]['bg_date'] != get_today_str_ve():
    db['users'][clean_user]['bg_date'] = get_today_str_ve()
    db['users'][clean_user]['bg_attempts'] = 0


# ==========================================
# === COMANDOS DE ADMINISTRACIÓN DE CAZA ===
# ==========================================

@bot.message_handler(commands=['comandos'])
def cmd_comandos(message):
  if not check_admin(message):
    return
  text = (
      "⚡ **LISTA DE TODOS LOS COMANDOS DE ADMINISTRACIÓN Y JUEGO** ⚡\n\n"
      "👑 **Administración (Solo Admin Suprema):**\n"
      "• `/starthunt` - Inicia la jornada de caza seleccionando grupo.\n"
      "• `/endhunt` - Finaliza la jornada de caza activa.\n"
      "• `/witch` (o `/bruja`) - Envía una bruja al grupo activo.\n"
      "• `/types` - Muestra la lista de tipos de brujas.\n"
      "• `/byewitch` (o `/cancel`) - Cancela la bruja activa.\n"
      "• `/give` - Añade caramelos a un usuario.\n"
      "• `/rest` - Resta caramelos a un usuario.\n"
      "• `/ban` - Sanciona temporalmente a un usuario.\n"
      "• `/topevent` - Muestra el top 20 de cazadores.\n"
      "• `/see` - Consulta los caramelos de un usuario.\n"
      "• `/chance` - Otorga intentos extra para Bat or Ghost.\n"
      "• `/graves` - Configura los valores de las tumbas.\n"
      "• `/extra` - Da partidas extra de Pennywise.\n"
      "• `/jack` - Da intentos extra de Blackjack.\n"
      "• `/comandos` - Muestra este panel de comandos.\n\n"
      "🎃 **Comandos de Usuario / Juegos:**\n"
      "• `/start` - Mensaje de bienvenida.\n"
      "• `/games` - Muestra el menú de juegos.\n"
      "• `/calabaza` - Consulta tus caramelos.\n"
      "• `/batghost` - Juega Bat or Ghost.\n"
      "• `/cementerio` - Abre una tumba del cementerio diario.\n"
      "• `/pennywise` - Juega al globo de Pennywise.\n"
      "• `/leave` - Retira tus ganancias en Pennywise.\n"
      "• `/blackjack` - Juega al blackjack de terror.\n"
      "• `/pedir` - Pide una carta adicional en blackjack.\n"
      "• `/retirarme` (o `/retirar`) - Cierra tu mano de blackjack.\n"
      "• `/coraline` - Juega con las puertas secretas de Coraline (máximo 3 veces al día).\n"
      "• `/shop` - Tienda de pociones y objetos mágicos.\n"
      "• `/buy` - Compra un artículo de la tienda.\n"
      "• `/items` - Consulta tu inventario de objetos.\n"
      "• `/envenenar` - Usa una poción venenosa contra otro jugador.\n"
      "• `/milagrosa` - Usa una poción milagrosa para robar caramelos.\n"
      "• `/ojos` - Juega al juego de los ojos.\n"
      "• `/slotween` - Juega a la tragamonedas de Halloween."
  )
  bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=['starthunt'])
def cmd_starthunt(message):
  if not check_admin(message):
    return
  markup = InlineKeyboardMarkup()
  markup.row(
      InlineKeyboardButton("cherry's", callback_data='set_group_cherrys'),
      InlineKeyboardButton('testing', callback_data='set_group_testing'),
  )
  bot.send_message(
      message.chat.id,
      'ㅤ⬚  selecciona el grupo para iniciar la jornada de caza:  ،͟,',
      reply_markup=markup,
  )


@bot.message_handler(commands=['endhunt'])
def cmd_endhunt(message):
  if not check_admin(message):
    return
  db['activeHunt']['active'] = False
  db['activeHunt']['targetGroup'] = None
  db['activeWitch'] = None
  bot.send_message(
      message.chat.id, 'ㅤ⬚  la jornada de caza ha finalizado con éxito.  ،͟,'
  )


@bot.message_handler(commands=['witch', 'bruja'])
def cmd_witch(message):
  if not check_admin(message):
    return
  if (
      not db['activeHunt']['active']
      or not db['activeHunt']['targetGroup']
  ):
    return bot.send_message(
        message.chat.id,
        'ㅤ⬚  debes iniciar la jornada y seleccionar un grupo usando /starthunt'
        ' primero.  ،͟,',
    )
  target_group_key = db['activeHunt']['targetGroup']
  target_chat_id = GROUPS.get(target_group_key)
  args = message.text.split()[1:]
  if not args:
    return bot.send_message(
        message.chat.id,
        'ㅤ⬚  por favor especifica el tipo de bruja. usa /types para ver las'
        ' opciones.  ،͟,',
    )
  type_input = args[0].lower()
  markup = InlineKeyboardMarkup()
  markup.add(InlineKeyboardButton('𖤐ㅤㅤcatch !', callback_data='catch_witch'))
  try:
    if type_input == 'misteriosa':
      if len(args) < 2 or not args[1].lstrip('-').isdigit():
        return bot.send_message(
            message.chat.id,
            'ㅤ⬚  formato incorrecto. ej: /witch misteriosa 100 o /witch'
            ' misteriosa -100  ،͟,',
        )
      amount = int(args[1])
      witch = WITCH_TYPES['misteriosa']
      sent_msg = bot.send_photo(
          target_chat_id,
          witch['photo'],
          caption=witch['caption'],
          reply_markup=markup,
      )
      db['activeWitch'] = {
          'type': 'misteriosa',
          'customAmount': amount,
          'caught': False,
          'messageId': sent_msg.message_id,
          'chatId': target_chat_id,
      }
      return bot.send_message(
          message.chat.id,
          f'ㅤ⬚  bruja misteriosa enviada exitosamente al grupo'
          f' {target_group_key}.  ،͟,',
      )

    witch_key = None
    for key, data in WITCH_TYPES.items():
      if data['name'] == type_input or key == type_input:
        witch_key = key
        break

    if not witch_key or witch_key == 'misteriosa':
      return bot.send_message(
          message.chat.id,
          'ㅤ⬚  tipo de bruja no válido. revisa /types para ver los tipos'
          ' existentes.  ،͟,',
      )

    witch = WITCH_TYPES[witch_key]
    sent_msg = bot.send_photo(
        target_chat_id,
        witch['photo'],
        caption=witch['caption'],
        reply_markup=markup,
    )
    db['activeWitch'] = {
        'type': witch_key,
        'reward': witch['reward'],
        'caught': False,
        'messageId': sent_msg.message_id,
        'chatId': target_chat_id,
    }
    bot.send_message(
        message.chat.id,
        f'ㅤ⬚  bruja {witch["name"]} enviada exitosamente al grupo'
        f' {target_group_key}.  ،͟,',
    )
  except Exception as e:
    bot.send_message(
        message.chat.id,
        'ㅤ⬚  error al enviar la bruja al grupo. Asegúrate de que el bot sea'
        f' administrador en el grupo. Error: {e}  ،͟,',
    )


@bot.message_handler(commands=['types'])
def cmd_types(message):
  if not check_admin(message):
    return
  response_text = (
      '   ⬚   ㅤ    𝗅𝗂𝗌𝗍𝖺 𝖽𝖾 𝖻𝗋𝗎𝗃𝖺𝗌 𝗒 𝗌𝗎𝗌 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌:   ،͟,\n\n'
      '• común = 20 caramelos.\n• bosque = 50 caramelos.\n• noche = 80'
      ' caramelos.\n• piromantica = 100 caramelos.\n• nigromante = 150'
      ' caramelos.\n• reina = 200 caramelos.\n• mítica = 400 caramelos.\n• madre'
      ' = 600 caramelos.\n• suprema = 1000 caramelos.\n• misteriosa +'
      ' [cantidad] = suma o resta caramelos.'
  )
  bot.send_message(message.chat.id, response_text)


@bot.message_handler(commands=['byewitch', 'cancel'])
def cmd_cancel(message):
  if not check_admin(message):
    return
  db['activeWitch'] = None
  bot.send_message(message.chat.id, 'ㅤ⬚  dinámica activa cancelada con éxito.  ،͟,')


@bot.message_handler(commands=['give'])
def cmd_give(message):
  if not check_admin(message):
    return
  args = message.text.split()[1:]
  if len(args) < 2 or not args[1].isdigit():
    return bot.send_message(
        message.chat.id,
        'ㅤ⬚  formato incorrecto. uso: /give @usuario cantidad  ،͟,',
    )
  target_user = sanitize_username(args[0])
  amount = int(args[1])
  init_user(target_user)
  db['users'][target_user]['caramelos'] += amount
  if db['users'][target_user]['caramelos'] < 0:
    db['users'][target_user]['caramelos'] = 0
  bot.send_message(
      message.chat.id,
      f"ㅤ⬚  se le han añadido {amount} caramelos a @{target_user}. total:"
      f" {db['users'][target_user]['caramelos']} caramelos.  ،͟,",
  )


@bot.message_handler(commands=['rest'])
def cmd_rest(message):
  if not check_admin(message):
    return
  args = message.text.split()[1:]
  if len(args) < 2 or not args[1].isdigit():
    return bot.send_message(
        message.chat.id,
        'ㅤ⬚  formato incorrecto. uso: /rest @usuario cantidad  ،͟,',
    )
  target_user = sanitize_username(args[0])
  amount = int(args[1])
  init_user(target_user)
  db['users'][target_user]['caramelos'] -= amount
  if db['users'][target_user]['caramelos'] < 0:
    db['users'][target_user]['caramelos'] = 0
  bot.send_message(
      message.chat.id,
      f"ㅤ⬚  se le han restado {amount} caramelos a @{target_user}. total:"
      f" {db['users'][target_user]['caramelos']} caramelos.  ،͟,",
  )


@bot.message_handler(commands=['ban'])
def cmd_ban(message):
  if not check_admin(message):
    return
  args = message.text.split()[1:]
  if len(args) < 2:
    return bot.send_message(
        message.chat.id,
        'ㅤ⬚  formato incorrecto. uso: /ban @usuario 1h/30m/60s  ،͟,',
    )
  target_user = sanitize_username(args[0])
  time_delta = parse_duration(args[1])
  if not time_delta:
    return bot.send_message(
        message.chat.id, 'ㅤ⬚  formato de tiempo no válido. ej: 1h, 30m, 60s  ،͟,'
    )
  init_user(target_user)
  db['users'][target_user]['bannedUntil'] = (
      datetime.datetime.now() + time_delta
  )
  bot.send_message(
      message.chat.id,
      f'ㅤ⬚  el usuario @{target_user} ha sido baneado de las dinámicas por'
      f' {args[1]}.  ،͟,',
  )


@bot.message_handler(commands=['topevent'])
def cmd_topevent(message):
  if not check_admin(message):
    return
  users_list = [
      {'username': u, 'caramelos': data['caramelos']}
      for u, data in db['users'].items()
  ]
  sorted_users = sorted(
      users_list, key=lambda x: x['caramelos'], reverse=True
  )[:20]
  if not sorted_users:
    return bot.send_message(
        message.chat.id, 'ㅤ⬚  aún no hay registros de usuarios con caramelos.  ،͟,'
    )
  response_text = (
      '   ⬚   ㅤ    𝗍𝗈𝗉 𝟤𝟢 𝖼𝖺𝗓𝖺𝖽𝗈𝗋𝖾𝗌 𝖽𝖾 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌:   ،͟,\n\n'
  )
  for idx, u in enumerate(sorted_users, 1):
    response_text += f"{idx}. @{u['username']} — {u['caramelos']} caramelos\n"
  bot.send_message(message.chat.id, response_text)


@bot.message_handler(commands=['see'])
def cmd_see(message):
  if not check_admin(message):
    return
  args = message.text.split()[1:]
  if not args:
    return bot.send_message(
        message.chat.id, 'ㅤ⬚  especifica el usuario. uso: /see @usuario  ،͟,'
    )
  target_user = sanitize_username(args[0])
  init_user(target_user)
  count = db['users'][target_user]['caramelos']
  bot.send_message(
      message.chat.id,
      f'ㅤ⬚  el usuario @{target_user} tiene un total de {count} caramelos.  ،͟,',
  )


# ==========================================
# === CALLBACKS GENERALES (BRUJAS Y GRUPOS) ===
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith('set_group_')
    or call.data == 'catch_witch'
)
def handle_general_callbacks(call):
  clicker_username = call.from_user.username
  if call.data.startswith('set_group_'):
    if (
        not clicker_username
        or clicker_username.lower() != ADMIN_USERNAME.lower()
    ):
      return bot.answer_callback_query(
          call.id,
          'ㅤ⬚  solo la admin suprema puede hacer esto.  ،͟,',
          show_alert=True,
      )
    group_choice = call.data.replace('set_group_', '')
    db['activeHunt']['active'] = True
    db['activeHunt']['targetGroup'] = group_choice
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        f'ㅤ⬚  jornada iniciada con éxito. el grupo activo es: {group_choice}'
        f' ({GROUPS[group_choice]})  ،͟,',
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
    )
    return

  if call.data == 'catch_witch':
    if not clicker_username:
      return bot.answer_callback_query(
          call.id, 'ㅤ⬚  necesitas un username para participar.  ،͟,', show_alert=True
      )
    if is_banned(clicker_username):
      return bot.answer_callback_query(
          call.id, 'ㅤ⬚  estás sancionado.  ،͟,', show_alert=True
      )
    if not db['activeWitch']:
      return bot.answer_callback_query(
          call.id,
          'ㅤ⬚  ¡la bruja ha escapado o no está disponible!  ،͟,',
          show_alert=True,
      )
    if db['activeWitch']['caught']:
      return bot.answer_callback_query(
          call.id, 'ㅤ⬚  ¡alguien más atrapó a esta bruja antes!  ،͟,', show_alert=True
      )

    db['activeWitch']['caught'] = True
    current_witch = db['activeWitch']
    db['activeWitch'] = None
    init_user(clicker_username, call.from_user.id)
    witch_data = WITCH_TYPES[current_witch['type']]

    if current_witch['type'] == 'misteriosa':
      amount = current_witch['customAmount']
      db['users'][clicker_username]['caramelos'] += amount
      if db['users'][clicker_username]['caramelos'] < 0:
        db['users'][clicker_username]['caramelos'] = 0
      new_caption = witch_data['caughtCaption'](clicker_username, amount)
    else:
      db['users'][clicker_username]['caramelos'] += current_witch['reward']
      if db['users'][clicker_username]['caramelos'] < 0:
        db['users'][clicker_username]['caramelos'] = 0
      new_caption = witch_data['caughtCaption'](clicker_username)

    bot.answer_callback_query(call.id, '¡has atrapado a la bruja!')
    try:
      empty_markup = InlineKeyboardMarkup()
      bot.edit_message_caption(
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          caption=new_caption,
          reply_markup=empty_markup,
      )
    except Exception as e:
      print('Error al actualizar bruja:', e)

# ==========================================
# === MENÚ PRINCIPAL Y DE JUEGOS ===
# ==========================================

@bot.message_handler(commands=['start'])
def send_start(message):
    init_user(message.from_user.username, message.from_user.id)
    text = (
        "⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿\x7f⠀ ¡𝗁𝗈𝗅𝖺, 𝗃𝗎𝗀𝖺𝖽𝗈𝗋! \n"
        "⠀⠀⠀⠀\⣿\x7f⢻⣿\x7f⢻\x7f     𝗈𝖿𝗂𝖼𝗂𝖺𝗅𝗆𝖾𝗇𝗍𝖾 𝖿𝗈𝗋𝗆𝖺𝗌 𝘱𝖺𝗋𝗍𝖾 𝖽𝖾 𝗅𝖺 \n"
        "⠀⠀⠀\⣿⣿\\\x7f\x7f\x7f     𝖼𝖺𝗌𝖺 𝖽𝖾𝗅 𝗍𝖾𝗋𝗋𝗈𝗋 𝖽𝖾 𝖼𝗁𝖾𝗋𝗋𝗒'𝗌. \n"
        "⠀⠀\⣿⣿⣿⣿\x7f⢻⣿⣿⣿    𝗍𝖾 𝖽𝖾𝗌𝖾𝗈 𝗆𝗎𝖼𝗁𝖺 𝗌𝗎𝖾𝗋𝗍𝖾 𝗒... \n"
        "⣠⣾⣿⣿⣿⣿⣿⣤\x7f\x7f    𝗉𝖺𝖼𝗂𝖾𝗇𝖼𝗂𝖺, 𝗍𝖺𝗆𝖻𝗂é𝗇. \n"
        "⢿\x7f⢿⣿⣿⣿⣿⣿⣿⣿\x7f⠀𝗌𝗈𝗒 𝗊𝗎𝗂é𝗇 𝗍𝖾 𝖺𝗒𝗎𝖽𝖺𝗋á 𝖺\n"
        "⠀⠀⠈⠿⠿\x7f⠙⢿⣿\\\x7f⠀  𝗅𝗅𝖾𝗀𝖺𝗋 𝖺𝗅 𝗍𝗈𝗉 1 𝖽𝖾𝗅 𝖾𝗏𝖾𝗇𝗍𝗈,\n"
        "ㅤㅤㅤㅤㅤㅤㅤㅤ𝗉𝖾𝗋𝗈 𝗇𝗈 𝗅𝖾𝗌 𝖽𝗂𝗀𝖺𝗌 𝖺 𝗅𝗈𝗌 𝖽𝖾𝗆á𝗌.\n\n"
        "ㅤㅤㅤsin más que decir,\n"
        "ㅤㅤㅤpuedes empezar a jugar los juegos\n"
        "ㅤㅤㅤㅤㅤㅤㅤde mi inventario,\n"
        "ㅤㅤㅤㅤconsultalos usando /games"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['games'])
def send_games(message):
  init_user(message.from_user.username, message.from_user.id)
  text = (
      "ㅤ𓉳ㅤㅤㅤㅤ𝓥𝖺𝗆𝗉'𝗌 𝗁𝖺𝗅𝗅𝗈𝗐𝖾𝖾𝗇 𝗍𝗈𝗈𝗅𝗌.\n\n"
      "ㅤ𖥻  /batghost  ↝  𝖾𝗅𝗂𝗀𝖾 𝖾𝗇𝗍𝗋𝖾 𝖻𝖺𝗍 𝗒 𝗀𝗁𝗈𝗌𝗍 𝘱𝖺𝗋𝖺 𝗀𝖺𝗇𝖺𝗋"
      " 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.\n"
      "ㅤ𖥻  /pennywise  ↝  𝗎𝗇 𝗍𝗋𝖺𝗍𝗈 𝖼𝗈𝗇 𝘱𝖾𝗇𝗇𝗒𝗐𝗂𝗌𝖾, ¡𝗀𝖺𝗇𝖺 𝗈 𝘱𝗂𝖾𝗋𝖽𝖾𝗅𝗈"
      " 𝗍𝗈𝖽𝗈!\n"
      "ㅤ𖥻  /blackjack ↝  𝗅𝗅𝖾𝗀𝖺 𝖺 𝗅𝖺 𝖼𝖺𝗇𝗍𝗂𝖽𝖺𝖽 𝖾𝗑𝖺𝖼𝗍𝖺 𝖽𝖾 𝖼𝖺𝗋𝗍𝖺𝗌 𝘱𝖺𝗋𝖺"
      " 𝗀𝖺𝗇𝖺𝗋 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.\n"
      "ㅤ𖥻  /coraline  ↝  𝖽𝖾𝖼𝗂𝖽𝖾 𝖾𝗇𝗍𝗋𝖾 𝗅𝖺𝗌 𝘱𝗎𝖾𝗋𝗍𝖺𝗌 𝗌𝖾𝖼𝗋𝖾𝗍𝖺𝗌,"
      " 𝗉𝗎𝖾𝖽𝖾𝗌 𝖾𝗇𝖼𝗈𝗇𝗍𝗋𝖺𝗋 𝗎𝗇𝖺 𝖿𝗈𝗋𝗍𝗎𝗇𝖺 𝗈 𝘱𝖾𝗋𝖽𝖾𝗋𝗅𝖺.\n"
      "ㅤ𖥻  /cementerio  ↝  𝗅𝖺𝗌 𝗍𝗎𝗆𝖻𝖺𝗌 𝖽𝖾 𝗏𝖺𝗆𝗉, 𝖾𝗅𝗂𝗃𝖾 𝗌𝖺𝖻𝗂𝖺𝗆𝖾𝗇𝗍𝖾.\n"
      "ㅤ𖥻  /slotween  ↝  𝖿𝗂𝗃𝖺 𝗍𝗎 𝗌𝗎𝖾𝗋𝗍𝖾 𝖾𝗇 𝖾𝗅 𝗍𝗋𝖺𝗀𝖺𝗉𝖾𝗋𝗋𝖺𝗌.\n"
      "ㅤ𖥻  /ojos  ↝  𝗍𝖾𝗇 𝖼𝗎𝗂𝖽𝖺𝖽𝗈 𝗒 𝖾𝗅𝗂𝗃𝖾 𝖾𝗅 𝗈𝗃𝗈 𝖼𝗈𝗋𝗋𝖾𝗀𝗍𝗈\n"
      "ㅤ𖥻  /shop  ↝  𝖼𝗈𝗆𝗉𝗋𝖺𝗅𝖾 𝖺 𝗅𝖺 𝖻𝗋𝗎𝗃𝖺 𝗅𝖺 𝗿𝗎𝖾 𝗇𝖾𝖼𝖾𝗌𝗂𝗍𝖾𝗌\n"
      "ㅤ𖥻  /items  ↝  consulta tu inventario de pociones"
  )
  bot.reply_to(message, text)


@bot.message_handler(commands=['calabaza'])
def cmd_calabaza(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(
        message, 'ㅤ⬚  necesitas un @username en Telegram para consultar tu calabaza.  ،͟,',
    )
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)
  total_caramelos = db['users'][clean_user]['caramelos']
  text = (
      'ㅤㅤㅤㅤㅤ༉‧ ⃟     ㅤㅤhi, player!ㅤㅤㅤ 🎃 ㅤㅤㅤㅤㅤㅤ\n'
      'ㅤㅤㅤhas consultado tu calabaza de dulces, \n'
      'ㅤㅤㅤla cual puedes llenar jugando diversas\n'
      'ㅤㅤㅤㅤㅤㅤ dinámicas en el canal.\n'
      f'ㅤㅤㅤㅤtu total es de: {total_caramelos} caramelos.'
  )
  bot.send_message(message.chat.id, text)


# ==========================================
# === BAT OR GHOST ===
# ==========================================
STICKER_GHOST = 'CAACAgEAAxkBAANlar63tvWWvSHXtOUc0cHn35-HNEsAAt8GAALOC_hFlvX8Pp9XVXM9BA'
STICKER_BAT = 'CAACAgEAAxkBAANjar63tM84r-jlsMIAAe72lnYeEdMtAAIiDAACKUX5RcwtojlNWzohPQQ'

OUTCOMES_CHOICES = [500, 300, 100, 0, -50, -100, 400]
OUTCOMES_WEIGHTS = [5, 15, 20, 25, 15, 10, 10]


@bot.message_handler(commands=['chance'])
def cmd_chance(message):
  if not check_admin(message):
    return
  args = message.text.split()[1:]
  if not args:
    return bot.send_message(
        message.chat.id, 'ㅤ⬚  formato incorrecto. uso: /chance @usuario  ،͟,'
    )
  target_user = sanitize_username(args[0])
  init_bg_user(target_user)
  db['users'][target_user]['extra_chances'] += 3
  bot.send_message(
      message.chat.id,
      f'ㅤ⬚  se le han otorgado 3 intentos extra para Bat or Ghost a'
      f' @{target_user}.  ،͟,',
  )


@bot.message_handler(commands=['batghost'])
def cmd_batghost(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(
        message, 'ㅤ⬚  necesitas un @username en Telegram para jugar.  ،͟,'
    )
  if is_banned(clicker):
    return bot.reply_to(
        message, 'ㅤ⬚  estás sancionado y no puedes participar por ahora.  ،͟,'
    )
  clean_clicker = sanitize_username(clicker)
  init_bg_user(clean_clicker, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  is_suprema = clean_clicker.lower() == ADMIN_USERNAME.lower()
  if not is_suprema:
    used = db['users'][clean_clicker]['bg_attempts']
    extra = db['users'][clean_clicker]['extra_chances']
    if used >= (3 + extra):
      return bot.reply_to(
          message,
          'ㅤ⬚  has agotado tus intentos diarios de Bat or Ghost. ¡Vuelve mañana'
          ' o pide un /chance!  ،͟,',
      )

  text = (
      f'ㅤ┊ ㅤㅤ𝖻𝗂𝖾𝗇𝗏𝖾𝗇𝗂𝖽𝗈, @{clean_clicker} 𝖺...ㅤㅤㅤㅤㅤㅤㅤㅤㅤ\n'
      'ㅤㅤㅤㅤ  ㅤㅤㅤ𝓑𝖺𝗍 ㅤorㅤ𝓖𝗁𝗈𝗌𝗍 ㅤ .ᐟ\n\n'
      'ㅤ ㅤ𝗉𝗎𝖾𝖽𝖾𝗌 𝖾𝗅𝖾𝗀𝗂𝗋 𝖾𝗇𝗍𝗋𝖾 𝗎𝗇 𝖼𝗎𝗋𝗂𝗈𝗌𝗈 𝖿𝖺𝗇𝗍𝖺𝗌𝗆𝖺 \n'
      'ㅤ ㅤ𝗒 𝗎𝗇 𝖾𝗌𝖼𝗎𝗋𝗋𝗂𝖽𝗂𝗓𝗈 𝗆𝗎𝗋𝖼𝗂é𝗅𝖺𝗀𝗈, 𝖺𝗆𝻰𝗈𝗌 𝖼𝖺𝗆𝗂𝗇𝗈𝗌\n'
      'ㅤㅤ 𝖽𝖾𝗉𝖺𝗋𝖺𝗇 𝗎𝗇𝖺 𝗋𝖾𝖼𝗈𝗆𝗉𝖾𝗇𝗌𝖺 𝘱𝖺𝗋𝖺 𝗍í, 𝘱𝖾𝗋𝗈...\n'
      'ㅤ ㅤ¿𝗌𝖾𝗋á 𝖻𝗎𝖾𝗇𝖺? ¡𝗇𝖺𝖽𝗂𝖾 𝗅𝗈 𝗌𝖺𝖻𝖾!ㅤㅤଘ(𖦹’⩊’).\n\n'
      "ㅤ ㅤㅤ 𝖾𝗌𝖼𝗋𝗂𝖻𝖾 '𝖻𝖺𝗍' 𝗈 '𝗀𝗁𝗈𝗌𝗍' 𝗌𝖾𝗀ú𝗇 𝗍𝗎 𝖾𝗅𝖾𝖼𝖼𝗂ó𝗇"
  )
  bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(
    func=lambda msg: msg.text
    and msg.text.strip().lower() in ['bat', 'ghost']
)
def handle_batghost_text_choice(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(
        message, 'ㅤ⬚  necesitas un @username en Telegram para jugar.  ،͟,'
    )
  clean_clicker = sanitize_username(clicker)
  if is_banned(clean_clicker):
    return bot.reply_to(message, 'ㅤ⬚  estás sancionado.  ،͟,')
  init_bg_user(clean_clicker, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  is_suprema = clean_clicker.lower() == ADMIN_USERNAME.lower()
  if not is_suprema:
    used = db['users'][clean_clicker]['bg_attempts']
    extra = db['users'][clean_clicker]['extra_chances']
    if used >= (3 + extra):
      return bot.reply_to(
          message, 'ㅤ⬚  has usado todos tus intentos disponibles por hoy.  ،͟,'
      )
    db['users'][clean_clicker]['bg_attempts'] += 1

  user_choice = message.text.strip().lower()
  vamp_choice = random.choice(['bat', 'ghost'])

  if user_choice != vamp_choice:
    if vamp_choice == 'ghost':
      bot.send_sticker(message.chat.id, STICKER_GHOST)
      text = (
          'ㅤㅤㅤㅤ⚝ㅤㅤ𝓥𝖺𝗆𝗉 𝖾𝗅𝗂𝗀𝗂ó 𝗀𝗁𝗈𝗌𝗍! ㅤㅤㅤㅤㅤㅤㅤㅤ\n'
          'ㅤㅤ𝗁𝖺 𝖽𝖾𝖼𝗂𝖽𝗂𝖽𝗈 𝗅𝗅𝖾𝗏𝖺𝗋𝗍𝖾 𝗅𝖺 𝖼𝗈𝗇𝗍𝗋𝖺𝗋𝗂𝖺 𝖾𝗌𝗍𝖺 𝗏𝖾𝗓. \n'
          'ㅤㅤㅤㅤㅤㅤ𝗍𝖾 𝗅𝗅𝖾𝗏𝖺𝗌: 0 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
      )
    else:
      bot.send_sticker(message.chat.id, STICKER_BAT)
      text = (
          'ㅤㅤㅤㅤㅤ⚝ㅤㅤ𝓥𝖺𝗆𝗉 𝖾𝗅𝗂𝗀𝗂ó 𝖻𝖺𝗍! ㅤㅤㅤㅤㅤㅤㅤㅤ\n'
          'ㅤㅤ𝗁𝖺 𝖽𝖾𝖼𝗂𝖽𝗂𝖽𝗈 𝗅𝗅𝖾𝗏𝖺𝗋𝗍𝖾 𝗅𝖺 𝖼𝗈𝗇𝗍𝗋𝖺𝗋𝗂𝖺 𝖾𝗌𝗍𝖺 𝗏𝖾𝗓. \n'
          'ㅤㅤㅤㅤㅤㅤ𝗍𝖾 𝗅𝗅𝖾𝗏𝖺𝗌: 0 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
      )
    return bot.send_message(message.chat.id, text)

  reward = random.choices(OUTCOMES_CHOICES, weights=OUTCOMES_WEIGHTS)[0]
  db['users'][clean_clicker]['caramelos'] += reward
  if db['users'][clean_clicker]['caramelos'] < 0:
    db['users'][clean_clicker]['caramelos'] = 0

  sticker = STICKER_GHOST if vamp_choice == 'ghost' else STICKER_BAT
  bot.send_sticker(message.chat.id, sticker)

  if reward == 0:
    text = (
        f'ㅤㅤㅤ ㅤㅤ⚝ㅤㅤ𝓥𝖺𝗆𝗉 𝖾𝗅𝗂𝗀𝗂ó {vamp_choice}!'
        ' ㅤㅤㅤㅤㅤㅤㅤㅤ\nㅤㅤ ㅤㅤ𝖼𝗈𝗂𝗇𝖼𝗂𝖽𝗂𝖾𝗋𝗈𝗇 𝖾𝗌𝗍𝖺 𝗏𝖾𝗓, 𝗉𝖾𝗋𝗈 𝗇𝗈'
        ' \nㅤ     ㅤ 𝗉𝖺𝗋𝖾𝗀𝖾 𝗊𝗎𝖾𝗋𝖾𝗋 𝖼𝖾𝖽𝖾𝗋 𝖽𝖾 𝗌𝗎𝗌'
        ' 𝖽𝗎𝗅𝖼𝖾𝗌.\nㅤㅤㅤㅤ  ㅤㅤ𝗍𝖾 𝗅𝗅𝖾𝗏𝖺𝗌: 0 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
    )
    bot.send_message(message.chat.id, text)
  elif reward < 0:
    loss = abs(reward)
    text = (
        f'ㅤㅤㅤ ㅤㅤ⚝ㅤㅤ𝓥𝖺𝗆𝗉 𝖾𝗅𝗂𝗀𝗂ó {vamp_choice}!'
        ' ㅤㅤㅤㅤㅤㅤㅤㅤ\nㅤㅤㅤ𝗒 𝗍𝖺𝗆𝖻𝗂é𝗇 𝗁𝖺 𝖾𝗅𝖾𝗀𝗂𝖽𝗈 𝗎𝗇𝖺'
        ' 𝗍𝗋𝖺𝗏𝖾𝗌𝗎𝗋𝖺.\nㅤㅤㅤㅤㅤ  𝗏𝖺𝗆𝗉... ¡𝗍𝖾 𝗁𝖺 𝗋𝗈𝖻𝖺𝖽𝗈! (๑´`๑)\nㅤㅤㅤㅤㅤ'
        f'   ㅤ𝗍𝖾 𝗊𝗎𝗂𝗍ó: {loss} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
    )
    bot.send_message(message.chat.id, text)
  else:
    texto = (
        f"        ⚝      𝓥𝖺𝗆𝗉 𝖾𝗅𝗂𝗀𝗂ó bat!        \n"
        f"      ¡𝖾𝗌𝗍á 𝖽𝖾 𝖻𝗎𝖾𝗇 𝗁𝗎𝗆𝗈𝗋 𝗁𝗈𝗒!\n"
        f"      𝗍𝖾 𝗁𝖺 𝖼𝖾𝖽𝗂𝖽𝗈 𝖺𝗅𝗀𝗎𝗇𝗈𝗌 𝖽𝖾 𝗌𝗎𝗌 𝖽𝗎𝗅𝖼𝖾𝗌.\n"
        f"      𝗈𝖻𝗍𝗎𝗏𝗂𝗌𝗍𝖾: {reward} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌."
    )
    bot.send_message(message.chat.id, texto)

# ==========================================
# === CEMENTERIO DE VAMP (Disponible siempre) ===
# ==========================================

@bot.message_handler(commands=['graves'])
def cmd_graves(message):
  if not check_admin(message):
    return
  args = message.text.split()[1:]
  if len(args) != 5:
    return bot.send_message(
        message.chat.id,
        'ㅤ⬚  formato incorrecto. Uso: /graves cant1 cant2 cant3 cant4 cant5'
        '  ،͟,',
    )
  try:
    values = [int(x) for x in args]
    db['graves_today'] = values
    bot.send_message(
        message.chat.id,
        f'ㅤ⬚  Valores de las tumbas actualizados para hoy: {values}  ،͟,',
    )
  except ValueError:
    bot.send_message(
        message.chat.id, 'ㅤ⬚  todas las cantidades deben ser números enteros.  ،͟,'
    )


@bot.message_handler(commands=['cementerio'])
def cmd_cementerio(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(
        message, 'ㅤ⬚  necesitas un @username en Telegram para jugar.  ،͟,'
    )
  clean_user = sanitize_username(clicker)
  init_game_users(clean_user, message.from_user.id)

  is_suprema = clean_user.lower() == ADMIN_USERNAME.lower()
  if not is_suprema and db['users'][clean_user]['graves_attempts'] >= 1:
    return bot.reply_to(
        message, 'ㅤ⬚  ya has abierto una tumba hoy. ¡Vuelve mañana!  ،͟,'
    )

  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(
          ' 𖥻   start.', callback_data=f'cemetery_start_{clean_user}'
      )
  )
  text = (
      'ㅤㅤㅤㅤ  ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ㅤㅤ⚰️ ㅤㅤ   ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ㅤㅤㅤㅤㅤㅤㅤ\n'
      'ㅤ༼ ㅤㅤ𝓥𝖺𝗆𝗉 𝗍𝖾 𝘱𝗋𝖾𝗌𝖾𝗇𝗍𝖺 5 𝖽𝖾 𝗌𝗎𝗌 𝗍𝗎𝗆𝖻𝖺𝗌...\n'
      'ㅤㅤㅤㅤㅤ¿𝗍𝖾 𝖺𝗋𝗋𝗂𝖾𝗌𝗀𝖺𝗌 𝖺 𝖺𝖻𝗋𝗂𝗋𝗅𝖺𝗌?  (՞  ܸ. .ܸ՞)︎'
  )
  bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cemetery_'))
def handle_cemetery_callbacks(call):
  parts = call.data.split('_')
  action = parts[1]
  owner_user = parts[2]
  clicker = call.from_user.username
  if not clicker:
    return bot.answer_callback_query(
        call.id, 'Necesitas un @username.', show_alert=True
    )
  clean_clicker = sanitize_username(clicker)
  if clean_clicker != owner_user:
    return bot.answer_callback_query(
        call.id,
        'ㅤ⬚  esta partida no te pertenece. Abre la tuya con /cementerio  ،͟,',
        show_alert=True,
    )

  init_game_users(clean_clicker, call.from_user.id)
  is_suprema = clean_clicker.lower() == ADMIN_USERNAME.lower()
  if action == 'start':
    if not is_suprema and db['users'][clean_clicker]['graves_attempts'] >= 1:
      return bot.answer_callback_query(
          call.id, 'ㅤ⬚  ya usaste tu intento diario.  ،͟,', show_alert=True
      )
    bot.answer_callback_query(call.id)
    try:
      bot.edit_message_reply_markup(
          chat_id=call.message.chat.id,
          message_id=call.message.message_id,
          reply_markup=None,
      )
    except Exception:
      pass

    shuffled_graves = db['graves_today'].copy()
    random.shuffle(shuffled_graves)
    markup = InlineKeyboardMarkup()
    buttons = []
    for i in range(5):
      val = shuffled_graves[i]
      buttons.append(
          InlineKeyboardButton(
              '⚰️', callback_data=f'cemopen_{i+1}_{val}_{clean_clicker}'
          )
      )
    markup.row(*buttons)
    text = (
        'ㅤㅤㅤ   ㅤ  ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ㅤㅤ⚰️ ㅤㅤ   ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ ̼ㅤㅤㅤㅤㅤㅤㅤ\n'
        'ㅤㅤ ༼ ㅤㅤ𝓥𝖺𝗆𝗉 𝖽𝖺 𝗎𝗇 𝘱𝖺𝗌𝗈 𝖺𝗍𝗋á𝗌, 𝖾𝗌 𝗍𝗎 𝗍𝗎𝗋𝗇𝗈.\n'
        'ㅤㅤ ㅤ𝖽𝖾𝻀𝖾𝗌 𝖾𝗅𝖾𝗀𝗂𝗋 𝗎𝗇𝖺 𝖽𝖾 𝗅𝖺𝗌 5 𝗍𝗎𝗆𝖻𝖺𝗌 𝗊𝗎𝖾 𝗌𝖾 \n'
        'ㅤㅤㅤㅤ𝗍𝖾 𝘱𝗋𝖾𝗌𝖾𝗇𝗍𝖺𝗇, 𝗁𝖺𝗒 𝗎𝗇𝖺𝗌 𝖻𝗎𝖾𝗇𝖺𝗌 𝗒 𝗈𝗍𝗋𝖺𝗌... \n'
        'ㅤㅤㅤ ㅤㅤㅤ𝗇𝗈 𝗍𝖺𝗇𝗍𝗈. ¡𝖽𝖾𝖼𝗂𝖽𝖾 𝗌𝖺𝖻𝗂𝖺𝗆𝖾𝗇𝗍𝖾!'
    )
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cemopen_'))
def handle_cemetery_open(call):
  parts = call.data.split('_')
  grave_num = parts[1]
  amount = int(parts[2])
  owner_user = parts[3]
  clicker = call.from_user.username
  clean_clicker = sanitize_username(clicker)

  if clean_clicker != owner_user:
    return bot.answer_callback_query(
        call.id, 'ㅤ⬚  esta partida no te pertenece.  ،͟,', show_alert=True
    )

  is_suprema = clean_clicker.lower() == ADMIN_USERNAME.lower()
  if not is_suprema and db['users'][clean_clicker]['graves_attempts'] >= 1:
    return bot.answer_callback_query(
        call.id, 'ㅤ⬚  ya usaste tu intento de hoy.  ،͟,', show_alert=True
    )
  if not is_suprema:
    db['users'][clean_clicker]['graves_attempts'] += 1

  bot.answer_callback_query(call.id)
  try:
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None,
    )
  except Exception:
    pass

  db['users'][clean_clicker]['caramelos'] += amount
  if db['users'][clean_clicker]['caramelos'] < 0:
    db['users'][clean_clicker]['caramelos'] = 0

  if amount >= 0:
    text = (
        f'ㅤ ʚ ⚰️ ɞ  ㅤㅤ ¡   𝖾𝗅𝖾𝗀𝗂𝗌𝗍𝖾 𝗅𝖺 𝗍𝗎𝗆𝖻𝖺 {grave_num}!   !\n\n'
        'ㅤㅤ  𝗒 𝗏𝖺𝗆𝗉, 𝗀𝖾𝗇𝖾𝗋𝗈𝗌𝗈, 𝖽𝖾𝖼𝗂𝖽𝗂ó 𝗈𝗍𝗈𝗋𝗀𝖺𝗋𝗍𝖾 𝗅𝗈𝗌 \n'
        'ㅤ  𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌 𝗊𝗎𝖾 ... ¿𝖺𝗅𝗀𝗎𝗂𝖾𝗇? 𝖽𝖾𝗃ó 𝗀𝗎𝖺𝗋𝖽𝖺𝖽𝗈𝗌\n'
        'ㅤㅤㅤ ㅤㅤㅤ  ㅤ   𝖾𝗇 𝖾𝗌𝖺 𝗍𝗎𝗆𝖻𝖺.\n\n'
        f'ㅤㅤ ㅤ ㅤ 𝗈𝖻𝗍𝗎𝗏𝗂𝗌𝗍𝖾: {amount} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. \n'
        'ㅤ  ¡ 𝗏𝗎𝖾𝗅𝗏𝖾 𝗆𝖺ñ𝖺𝗇𝖺 𝗉𝖺𝗋𝖺 𝗏𝗈𝗅𝗏𝖾𝗋 𝖺 𝗃𝗎𝗀𝖺𝗋 !'
    )
  else:
    loss = abs(amount)
    text = (
        f'ㅤ ʚ ⚰️ ɞ  ㅤㅤ ¡   𝖾𝗅𝖾𝗀𝗂𝗌𝗍𝖾 𝗅𝖺 𝗍𝗎𝗆𝖻𝖺 {grave_num}!   !\n\n'
        'ㅤㅤ 𝗒 𝗏𝖺𝗆𝗉, 𝚌𝚘𝚗 𝗎𝗇𝖺 𝗌𝗈𝗇𝗋𝗂𝗌𝖺 𝖻𝗎𝗋𝗅𝗈𝗇𝖺 𝗍𝖾 \n'
        'ㅤ 𝗆𝗎𝖾𝗌𝗍𝗋𝖺. ... ¡ 𝗊𝗎𝖾  𝗇𝗈 𝗁𝖺𝗒 𝗇𝖺𝖽𝖺 ! 𝗒,\n'
        f'ㅤ  𝗉𝖺𝗋𝖺  𝖼𝗈𝗅𝗆𝗈 , 𝗍𝖾 𝗁𝖺 𝗊𝗎𝗂𝗍𝖺𝖽𝗈 {loss} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌 .\n\n'
        'ㅤ   ¡  𝗏𝗎𝖾𝗅𝗏𝖾 𝗆𝖺ñ𝖺𝗇𝖺  𝗉𝖺𝗋𝖺 𝗏𝗈𝗅𝗏𝖾𝗋 𝖺 𝗃𝗎𝗀𝖺𝗋 !'
    )
  bot.send_message(call.message.chat.id, text)


# ==========================================
# === PENNYWISE'S BALLOON ===
# ==========================================

@bot.message_handler(commands=['extra'])
def cmd_extra(message):
  if not check_admin(message):
    return
  args = message.text.split()[1:]
  if not args:
    return bot.send_message(
        message.chat.id, 'ㅤ⬚  formato incorrecto. uso: /extra @usuario  ،͟,'
    )
  target_user = sanitize_username(args[0])
  init_game_users(target_user)
  db['users'][target_user]['penny_extra'] += 1
  bot.send_message(
      message.chat.id,
      f'ㅤ⬚  se le ha otorgado +1 partida extra de Pennywise a @{target_user}.'
      '  ،͟,',
  )


@bot.message_handler(commands=['pennywise'])
def cmd_pennywise(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(
        message, 'ㅤ⬚  necesitas un @username en Telegram para jugar.  ،͟,'
    )
  if is_banned(clicker):
    return bot.reply_to(message, 'ㅤ⬚  estás sancionado.  ،͟,')
  clean_user = sanitize_username(clicker)
  init_game_users(clean_user, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  args = message.text.split()[1:]
  if not args or not args[0].isdigit():
    return bot.reply_to(
        message,
        'ㅤ⬚  debes especificar el monto a apostar. Uso: /pennywise <apuesta> '
        ' ،͟,',
    )

  bet = int(args[0])
  if bet <= 0:
    return bot.reply_to(message, 'ㅤ⬚  la apuesta debe ser mayor a 0.  ،͟,')

  user_caramelos = db['users'][clean_user]['caramelos']
  if user_caramelos < bet:
    return bot.reply_to(message, 'ㅤ⬚  no tienes suficientes caramelos  ،͟,')

  is_suprema = clean_user.lower() == ADMIN_USERNAME.lower()
  if not is_suprema:
    used = db['users'][clean_user]['penny_attempts']
    extra = db['users'][clean_user]['penny_extra']
    if used >= (1 + extra):
      return bot.reply_to(
          message,
          'ㅤ⬚  ya usaste tu partida de Pennywise por hoy. ¡Vuelve mañana o pide'
          ' un /extra!  ،͟,',
      )
    db['users'][clean_user]['penny_attempts'] += 1

  db['users'][clean_user]['caramelos'] -= bet
  if db['users'][clean_user]['caramelos'] < 0:
    db['users'][clean_user]['caramelos'] = 0
    
  db['users'][clean_user]['penny_active'] = {
      'bet': bet,
      'profit': bet,
      'pins': 0,
  }

  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(' 𖥻   pinch.', callback_data=f'pny_pinch_{clean_user}')
  )
  text = (
      'ㅤㅤㅤㅤ🎈ㅤㅤㅤ𝓟𝖾𝗇𝗇𝗒𝗐𝗂𝗌𝖾\'𝗌 𝖻𝖺𝗅𝗅𝗈𝗈𝗇ㅤㅤㅤˊ˗ㅤㅤㅤㅤㅤㅤ\n\n'
      f'ㅤㅤ𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗅: {bet}\n'
      'ㅤㅤ𝗉𝗂𝗇𝖼𝗁𝖺𝗓𝗈𝗌: \n'
      f'ㅤㅤ𝗀𝖺𝗇𝖺𝗇𝖼𝗂𝖺𝗌: {bet}\n\n'
      'ㅤㅤㅤ𝗎𝗌𝖺 /leave 𝖼𝗎𝖺𝗇𝖽𝗈 𝗊𝗎𝗂𝖾𝗋𝖺𝗌 𝗋𝖾𝗍𝗂𝗋𝖺𝗋 𝗍𝗎𝗌 𝗀𝖺𝗇𝖺𝗇𝖼𝗂𝖺𝗌.\n'
      'ㅤㅤㅤㅤ𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝗏𝗈𝗍ó𝗇 𝗉𝖺𝗋𝖺 𝗉𝗂𝗇𝖼𝗁𝖺𝗋 𝖽𝖾 𝗇𝗎𝖾𝗏𝗈.'
  )
  bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('pny_pinch_'))
def handle_penny_pinch(call):
  owner_user = call.data.split('_')[2]
  clicker = call.from_user.username
  clean_clicker = sanitize_username(clicker)
  if clean_clicker != owner_user:
    return bot.answer_callback_query(
        call.id, 'ㅤ⬚  esta partida no te pertenece.  ،͟,', show_alert=True
    )

  game_state = db['users'][clean_clicker]['penny_active']
  if not game_state:
    return bot.answer_callback_query(
        call.id, 'ㅤ⬚  no tienes ninguna partida activa.  ،͟,', show_alert=True
    )

  bot.answer_callback_query(call.id)
  try:
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None,
    )
  except Exception:
    pass

  outcomes = ['BOOM', 'NADA', 'MITAD', 'DUPLICAR', 'TRIPLICAR']
  weights = [30, 25, 25, 15, 5]
  result = random.choices(outcomes, weights=weights)[0]

  if result == 'BOOM':
    db['users'][clean_clicker]['penny_active'] = None
    text = (
        'ㅤㅤㅤㅤ🎈ㅤㅤㅤ𝓟𝖾𝗇𝗇𝗒𝗐𝗂𝗌𝖾\'𝗌 𝖻𝖺𝗅𝗅𝗈𝗈𝗇ㅤㅤㅤˊ˗ㅤㅤㅤㅤㅤㅤ\n\n'
        'ㅤㅤㅤㅤ¡𝗕𝗢𝗢𝗠! 𝖿𝖾𝗅𝗂𝖼𝗂𝖽𝖺𝖽𝖾𝗌, 𝗉𝗂𝗇𝖼𝗁𝖺𝗌𝗍𝖾 𝖾𝗅 𝗀𝗅𝗈𝖻𝗈.\n'
        'ㅤㅤㅤㅤ𝗉𝖾𝗇𝗇𝗒𝗐𝗂𝗌𝖾 𝗍𝗈𝗆𝖺 𝗍𝗈𝖽𝖺𝗌 𝗍𝗎𝗌 𝗀𝖺𝗇𝖺𝗇𝖼𝗂𝖺𝗌, \n'
        'ㅤㅤㅤㅤ𝖾𝗌 𝗎𝗇𝖺 𝗅á𝗌𝗍𝗂𝗆𝖺....\n\n'
        'ㅤㅤㅤㅤㅤㅤㅤ𝗉𝗋𝖾𝗆𝗂𝗈 𝖿𝗂𝗇𝖺𝗅: 0 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
    )
    return bot.send_message(call.message.chat.id, text)

  bet = game_state['bet']
  game_state['pins'] += 1
  if result == 'MITAD':
    game_state['profit'] += int(bet * 0.5)
  elif result == 'DUPLICAR':
    game_state['profit'] += bet * 2
  elif result == 'TRIPLICAR':
    game_state['profit'] += bet * 3

  pins_str = '📌' * game_state['pins']
  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton(' 𖥻   pinch.', callback_data=f'pny_pinch_{clean_clicker}')
  )
  text = (
      'ㅤㅤㅤㅤ🎈ㅤㅤㅤ𝓟𝖾𝗇𝗇𝗒𝗐𝗂𝗌𝖾\'𝗌 𝖻𝖺𝗅𝗅𝗈𝗈𝗇ㅤㅤㅤˊ˗ㅤㅤㅤㅤㅤㅤ\n\n'
      f'ㅤㅤ𝖺𝗉𝗎𝖾𝗌𝗍𝖺 𝗂𝗇𝗂𝖼𝗂𝖺𝗅: {bet}\n'
      f'ㅤㅤ𝗉𝗂𝗇𝖼𝗁𝖺𝗓𝗈𝗌: {pins_str}\n'
      f"ㅤㅤ𝗀𝖺𝗇𝖺𝗇𝖼𝗂𝖺𝗌: {game_state['profit']}\n\n"
      'ㅤㅤㅤ𝗎𝗌𝖺 /leave 𝖼𝗎𝖺𝗇𝖽𝗈 𝗊𝗎𝗂𝖾𝗋𝖺𝗌 𝗋𝖾𝗍𝗂𝗋𝖺𝗋 𝗍𝗎𝗌 𝗀𝖺𝗇𝖺𝗇𝖼𝗂𝖺𝗌.\n'
      'ㅤㅤㅤㅤ𝗉𝗋𝖾𝗌𝗂𝗈𝗇𝖺 𝖾𝗅 𝗏𝗈𝗍ó𝗇 𝗉𝖺𝗋𝖺 𝗉𝗂𝗇𝖼𝗁𝖺𝗋 𝖽𝖾 𝗇𝗎𝖾𝗏𝗈.'
  )
  bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.message_handler(commands=['leave'])
def cmd_leave(message):
  clicker = message.from_user.username
  if not clicker:
    return
  clean_user = sanitize_username(clicker)
  init_game_users(clean_user, message.from_user.id)
  game_state = db['users'][clean_user]['penny_active']
  if not game_state:
    return bot.reply_to(
        message, 'ㅤ⬚  no tienes ninguna partida activa de Pennywise.  ،͟,'
    )

  profit = game_state['profit']
  db['users'][clean_user]['caramelos'] += profit
  if db['users'][clean_user]['caramelos'] < 0:
    db['users'][clean_user]['caramelos'] = 0
    
  db['users'][clean_user]['penny_active'] = None
  text = (
      'ㅤㅤㅤㅤ🎈ㅤㅤㅤ𝓟𝖾𝗇𝗇𝗒𝗐𝗂𝗌𝖾\'𝗌 𝖻𝖺𝗅𝗅𝗈𝗈𝗇ㅤㅤㅤˊ˗ㅤㅤㅤㅤㅤㅤ\n\n'
      'ㅤㅤㅤㅤ¡𝗁𝖺𝗌 𝖽𝖾𝖼𝗂𝖽𝗂𝖽𝗈 𝗋𝖾𝗍𝗂𝗋𝖺𝗋𝗍𝖾 𝖺 𝗍𝗂𝖾𝗆𝗉𝗈!\n'
      'ㅤㅤ   𝗉𝖾𝗇𝗇𝗒𝗐𝗂𝗌𝖾 𝗍𝖾 𝗆𝗂𝗋𝖺 𝖼𝗈𝗇 𝗌𝗈𝗇𝗋𝗂𝗌𝖺 𝖻𝗎𝗋𝗅𝗈𝗇𝖺...\n\n'
      f'ㅤㅤㅤㅤㅤㅤㅤ𝗉𝗋𝖾𝗆𝗂𝗈 𝖿𝗂𝗇𝖺𝗅: {profit} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
  )
  bot.send_message(message.chat.id, text)


# ==========================================
# === JUEGO: BLACKJACK ===
# ==========================================
SUITS = ['♥', '♦', '♣', '♠']

@bot.message_handler(commands=['blackjack'])
def start_blackjack(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(
        message, 'ㅤ⬚  necesitas un @username en Telegram para jugar.  ،͟,'
    )
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  balance = db['users'][clean_user]['caramelos']
  if balance <= 0:
    return bot.reply_to(message, 'ㅤ⬚  no tienes suficientes caramelos  ،͟,')

  if db['users'][clean_user]['attempts'] <= 0:
    return bot.reply_to(
        message, '¡Te has quedado sin intentos diarios para este juego!'
    )

  db['users'][clean_user]['attempts'] -= 1
  initial_cards = random.randint(1, 21)
  db['users'][clean_user]['blackjack'] = {
      'total': initial_cards,
      'active': True,
  }

  text = (
      'ㅤㅤㅤㅤ┊ 🃏 ┆ㅤㅤ𝖻𝗅𝖺𝖼𝗄𝗃𝖺𝖼𝗄 𝗂𝗇𝗂𝖼𝗂𝖺𝖽𝗈.ㅤㅤㅤㅤㅤㅤㅤㅤ\n\n'
      f'ㅤㅤㅤ𝗂𝗇𝗂𝖼𝗂𝖺𝗌𝗍𝖾 𝖼𝗈𝗇: {initial_cards}.\n'
      'ㅤㅤㅤ𝖽𝖾𝖻𝖾𝗌 𝗉𝖾𝖽𝗂𝗋 𝗁𝖺𝗌𝗍𝖺 𝗅𝗅𝖾𝗀𝖺𝗋 𝖺 21 𝘱𝖺𝗋𝖺 𝖺𝗌í \n'
      'ㅤㅤㅤ𝗀𝖺𝗇𝖺𝗋, 𝗉𝖾𝗋𝗈, ¡𝗍𝖾𝗇 𝖼𝗎𝗂𝖽𝖺𝖽𝗈! 𝗌𝗂 𝗍𝖾 𝗉𝖺𝗌𝖺𝗌, \n'
      'ㅤㅤㅤ𝗏𝖺𝗆𝗉 𝗇𝗈 𝗍𝖾𝗇𝖽𝗋á 𝘱𝗂𝖾𝖽𝖺𝖽 𝖼𝗈𝗇𝗍𝗂𝗀𝗈.\n\n'
      ' 𝗎𝗌𝖺 /pedir 𝗉𝖺𝗋𝖺 𝗌𝗎𝗆𝖺𝗋 𝗒 /retirarme 𝗼𝗎𝗂𝖾𝗋𝖺𝗌 𝖼𝖾𝗋𝗋𝖺𝗋.'
  )
  bot.reply_to(message, text)


@bot.message_handler(commands=['pedir'])
def blackjack_pedir(message):
  clicker = message.from_user.username
  if not clicker:
    return
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  user = db['users'][clean_user]
  if not user.get('blackjack') or not user['blackjack']['active']:
    return bot.reply_to(
        message,
        'No tienes ninguna partida de blackjack activa. Usa /blackjack para'
        ' empezar.',
    )

  card_val = random.randint(1, 10)
  card_suit = random.choice(SUITS)
  card_str = f'{card_val}{card_suit}'
  user['blackjack']['total'] += card_val
  total = user['blackjack']['total']

  if total > 21:
    user['blackjack']['active'] = False
    text = (
        'ㅤ┊ 🃏 ┆ㅤ𝗏𝖺𝗆𝗉 𝗌𝖺𝖼𝖺 𝗎𝗇𝖺 𝖼𝖺𝗋𝗍𝖺 𝖽𝖾𝗅 𝗆𝖺𝗓𝗈 𝘱𝖺𝗋𝖺'
        ' 𝗍í.ㅤㅤㅤㅤㅤㅤ\n\n'
        f'ㅤ  ⎯ ㅤㅤ𝗍𝖾 𝗁𝖺 𝖽𝖺𝖽𝗈: {card_str} \n'
        f'ㅤ  ⎯ ㅤㅤ𝗍𝗂𝖾𝗇𝖾𝗌: {total}\n'
        '¡𝗈𝗈𝗉𝗌! 𝗍𝖾 𝗉𝖺𝗌𝖺𝗌𝗍𝖾 𝖽𝖾 21. 𝗌𝗎𝖾𝗋𝗍𝖾 𝘱𝖺𝗋𝖺 𝗅𝖺 𝗉𝗋ó𝗑𝗂𝗆𝖺.'
    )
  else:
    text = (
        'ㅤ┊ 🃏 ┆ㅤ𝗏𝖺𝗆𝗉 𝗌𝖺𝖼𝖺 𝗎𝗇𝖺 𝖼𝖺𝗋𝗍𝖺 𝖽𝖾𝗅 𝗆𝖺𝗓𝗈 𝘱𝖺𝗋𝖺'
        ' 𝗍í.ㅤㅤㅤㅤㅤㅤ\n\n'
        f'ㅤ  ⎯ ㅤㅤ𝗍𝖾 𝗁𝖺 𝖽𝖺𝖽𝗈: {card_str} \n'
        f'ㅤ  ⎯ ㅤㅤ𝗍𝗂𝖾𝗇𝖾𝗌: {total}\n'
        '𝗎𝗌𝖺 /pedir 𝗉𝖺𝗋𝖺 𝗌𝗎𝗆𝖺𝗋 𝗒 /retirarme 𝖼𝗎𝖺𝗇𝖽𝗈 𝗊𝗎𝗂𝖾𝗋𝖺𝗌 𝖼𝖾𝗋𝗋𝖺𝗋.'
    )
  bot.reply_to(message, text)


@bot.message_handler(commands=['retirar', 'retirarme'])
def blackjack_retirar(message):
  clicker = message.from_user.username
  if not clicker:
    return
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  user = db['users'][clean_user]
  if not user.get('blackjack') or not user['blackjack']['active']:
    return bot.reply_to(message, 'No tienes ninguna partida activa para retirar.')

  total = user['blackjack']['total']
  user['blackjack']['active'] = False

  if total == 21:
    user['caramelos'] += 300
    if user['caramelos'] < 0:
      user['caramelos'] = 0
    text = (
        'ㅤㅤ┊ 🃏 ┆ㅤ𝗏𝖺𝗆𝗉 𝖼𝗎𝖾𝗇𝗍𝖺 𝗍𝗎𝗌 𝖼𝖺𝗋𝗍𝖺𝗌...ㅤㅤㅤㅤㅤㅤ\n'
        'ㅤㅤㅤ ㅤㅤ   ㅤㅤ¡𝗎𝗇 21 𝗉𝖾𝗋𝖿𝖾𝖼𝗍𝗈!\n\n'
        'ㅤ𝗁𝖺𝗌 𝗀𝖺𝗇𝖺𝖽𝗈 𝖾𝗅 𝘱𝗋𝖾𝗆𝗂𝗈 𝗆𝖺𝗒𝗈𝗋, 300 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
    )
  elif total == 20:
    user['caramelos'] += 150
    if user['caramelos'] < 0:
      user['caramelos'] = 0
    text = (
        'ㅤㅤ┊ 🃏 ┆ㅤ𝗏𝖺𝗆𝗉 𝖼𝗎𝖾𝗇𝗍𝖺 𝗍𝗎𝗌 𝖼𝖺𝗋𝗍𝖺𝗌...ㅤㅤㅤㅤㅤㅤ\n'
        'ㅤㅤㅤㅤㅤㅤㅤ𝗍𝗂𝖾𝗇𝖾𝗌... 20 𝖼𝖺𝗋𝗍𝖺𝗌.\n\n'
        'ㅤㅤ𝗇𝗈 𝖾𝗌 𝗅𝗈 𝗊𝗎𝖾 𝗉𝗂𝖽𝗂ó, 𝗉𝖾𝗋𝗈 𝗍𝖾 𝖼𝖾𝖽𝖾 150 \n'
        'ㅤㅤㅤㅤ𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌 𝘱𝖺𝗋𝖺 𝗍𝗎 𝖾𝗌𝖿𝗎𝖾𝗋𝗓𝗈.'
    )
  else:
    text = (
        'ㅤㅤ┊ 🃏 ┆ㅤ𝗏𝖺𝗆𝗉 𝖼𝗎𝖾𝗇𝗍𝖺 𝗍𝗎𝗌 𝖼𝖺𝗋𝗍𝖺𝗌...ㅤㅤㅤㅤㅤㅤ\n'
        f'ㅤㅤㅤㅤㅤ 𝗎𝗁𝗆, ¿{total} 𝖼𝖺𝗋𝗍𝖺𝗌?\n\n'
        'ㅤㅤ𝗇𝗈 𝚙𝚞𝚎𝚍𝚎 𝚛𝚎𝚌𝚘𝚖𝚙𝚎𝚗𝚜𝚊𝚛𝚝𝚎 𝚙𝚘𝚛 𝚎𝚜𝗈...\n'
        'ㅤㅤㅤㅤㅤㅤ ¡𝚕𝚘 𝚜𝚎𝚗𝚝𝚒𝚖𝚘𝚜!'
    )
  bot.reply_to(message, text)


@bot.message_handler(commands=['jack'])
def admin_jack(message):
  if not check_admin(message):
    return
  if message.reply_to_message:
    target_username = sanitize_username(
        message.reply_to_message.from_user.username
    )
    if target_username:
      init_user(target_username)
      db['users'][target_username]['attempts'] += 5
      bot.reply_to(
          message,
          f'¡Se han otorgado 5 intentos adicionales a @{target_username}!',
      )
    else:
      bot.reply_to(
          message,
          'El usuario al que respondes no tiene un username válido configurado.',
      )
  else:
    bot.reply_to(
        message,
        'Responde al mensaje del usuario al que deseas darle 5 intentos con'
        ' /jack',
    )


# ==========================================
# === JUEGO: CORALINE ===
# ==========================================
STICKER_CORALINE = 'CAACAgEAAxkBAANnasGFhRZALzJAQV7zCuFXWTOV22UAAiwTAAJlmBFG5VLVBpbKY-E9BA'

@bot.message_handler(commands=['coraline'])
def start_coraline(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(
        message, 'ㅤ⬚  necesitas un @username en Telegram para jugar.  ،͟,'
    )
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  today = get_today_str_ve()
  if 'coraline_date' not in db['users'][clean_user] or db['users'][clean_user]['coraline_date'] != today:
    db['users'][clean_user]['coraline_date'] = today
    db['users'][clean_user]['coraline_daily_uses'] = 0

  if db['users'][clean_user]['coraline_daily_uses'] >= 3:
    return bot.reply_to(
        message, 'ㅤ⬚  has alcanzado el límite de 3 usos diarios para el juego de Coraline. ¡Vuelve mañana!  ،͟,'
    )

  db['users'][clean_user]['coraline_daily_uses'] += 1

  text = (
      'ㅤㅤㅤ - ̗̀ㅤ  🚪   ̖́-ㅤㅤ¡𝗁𝗈𝗅𝖺 𝖽𝖾 𝗇𝗎𝖾𝗏𝗈!ㅤㅤㅤㅤㅤㅤㅤㅤ\n\n'
      'ㅤㅤ𝖾𝗌 𝗎𝗇 𝘱𝗅𝖺𝖼𝖾𝗋 𝗍𝖾𝗇𝖾𝗋𝗍𝖾 𝖺𝗊𝗎í. 𝗁𝗈𝗒 𝖺𝖼𝗈𝗆𝘱𝖺ñ𝖺𝗋á𝗌 \n'
      'ㅤㅤ𝖺 𝗇𝗎𝖾𝗌𝗍𝗋𝖺 𝖺𝗆𝗂𝗀𝖺 𝖼𝗈𝗋𝖺𝗅𝗂𝗇𝖾 𝖺 𝖾𝗌𝖼𝖺𝗉𝖺𝗋, 𝖽𝖾𝖻𝖾𝗋á𝗌\n'
      'ㅤㅤ𝗍𝗈𝗆𝖺𝗋 𝖽𝗂𝖿í𝖼𝗂𝗅𝖾𝗌 𝖽𝖾𝖼𝗂𝗌𝗂𝗈𝗇𝖾𝗌... ¡𝖼𝗈𝗇𝖿𝗂𝖺𝗆𝗈𝗌 𝖾𝗇 𝗍𝗂!\n\n'
      'ㅤㅤㅤㅤㅤ𝖿𝗋𝖾𝗇𝗍𝖾 𝖺 𝗍í, 𝗁𝖺𝗒 𝖼𝗎𝖺𝗍𝗋𝗈 𝘱𝗎𝖾𝗋𝗍𝖺𝗌... \n'
      'ㅤㅤ𝗍𝗈𝖽𝖺𝗌 𝗍𝗂𝖾𝗇𝖾𝗇 𝗎𝗇 𝖽𝗂𝖿𝖾𝗋𝖾𝗇𝗍𝖾 𝖽𝖾𝗌𝗍𝗂𝗇𝗈, 𝖽𝖾𝗌𝖽𝖾 𝗅𝗈 \n'
      'ㅤㅤ𝗻𝗎𝖾𝗇𝗈 𝗁𝖺𝗌𝗍𝖺 𝗅𝗈 𝗍𝖾𝗋𝗋𝗂𝖻𝗅𝖾. ¡𝖾𝗅𝗂𝗀𝖾 𝗎𝗇𝖺 𝗌𝖺𝖻𝗂𝖺𝗆𝖾𝗇𝗍𝖾!'
  )
  markup = InlineKeyboardMarkup(row_width=4)
  markup.add(
      InlineKeyboardButton('𝟭', callback_data=f'door_1_{clean_user}'),
      InlineKeyboardButton('𝟐', callback_data=f'door_2_{clean_user}'),
      InlineKeyboardButton('𝟑', callback_data=f'door_3_{clean_user}'),
      InlineKeyboardButton('𝟒', callback_data=f'door_4_{clean_user}'),
  )
  bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('door_'))
def handle_coraline_door(call):
  data_parts = call.data.split('_')
  door_num = data_parts[1]
  owner_username = data_parts[2]
  clicker = call.from_user.username
  clean_clicker = sanitize_username(clicker)

  if clean_clicker != owner_username:
    return bot.answer_callback_query(
        call.id,
        '¡No puedes tocar las puertas de la partida de otro jugador!',
        show_alert=True,
    )

  init_user(clean_clicker, call.from_user.id)
  user = db['users'][clean_clicker]
  outcome = random.choice(['win', 'win', 'lose', 'nothing'])
  bot.send_sticker(call.message.chat.id, STICKER_CORALINE)

  if outcome == 'win':
    cantidad = random.randint(100, 1000)
    user['caramelos'] += cantidad
    if user['caramelos'] < 0:
      user['caramelos'] = 0
    msg = (
        f'ㅤㅤ - ̗̀ㅤ  🚪   ̖́-ㅤㅤ𝗁𝖺𝗌 𝖾𝗅𝖾𝗀𝗂𝖽𝗈 𝗅𝖺 𝘱𝗎𝖾𝗋𝗍𝖺'
        f' {door_num}ㅤㅤㅤㅤㅤ\n\n'
        'ㅤㅤㅤㅤㅤ¡𝖻𝗎𝖾𝗇𝖺 𝖾𝗅𝖾𝖼𝖼𝗂ó𝗇! 𝖾𝗇𝖼𝗈𝗇𝗍𝗋𝖺𝗌𝗍𝖾 𝗎𝗇 \n'
        f'ㅤㅤㅤ𝗆𝗈𝗇𝗍ó𝗇 𝖽𝖾 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌, 𝗁𝖺𝗌 𝗌𝗎𝗆𝖺𝖽𝗈 {cantidad}.'
    )
  elif outcome == 'lose':
    cantidad = random.randint(100, 400)
    user['caramelos'] = max(0, user['caramelos'] - cantidad)
    msg = (
        f'ㅤㅤ - ̗̀ㅤ  🚪   ̖́-ㅤㅤ𝗁𝖺𝗌 𝖾𝗅𝖾𝗀𝗂𝖽𝗈 𝗅𝖺 𝘱𝗎𝖾𝗋𝗍𝖺'
        f' {door_num}ㅤㅤㅤㅤ\n\n'
        'ㅤㅤㅤㅤㅤ𝗏𝖺𝗒𝖺... 𝖾𝗌 𝗎𝗇𝖺 𝘱𝖾𝗇𝖺. 𝗎𝗇 𝗆𝗈𝗎𝗇𝗌𝗍𝗋𝗈 \n'
        'ㅤ   𝖽𝖾𝗅 𝗈𝗍𝗋𝗈 𝗅𝖺𝖽𝗈 𝗌𝖾 𝗅𝗅𝖾𝗏ó 𝗽𝖺𝗋𝗍𝖾 𝖽𝖾 𝗍𝗎𝗌 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌, \n'
        f'ㅤㅤㅤㅤㅤㅤㅤㅤ𝖾𝗑𝖺𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾 {cantidad}.'
    )
  else:
    msg = (
        f'ㅤㅤ - ̗̀ㅤ     ̖́-ㅤㅤ𝗁𝖺𝗌 𝖾𝗅𝖾𝗀𝗂𝖽𝗈 𝗅𝖺 𝘱𝗎𝖾𝗋𝗍𝖺'
        f' {door_num}ㅤㅤㅤㅤㅤ\n\n'
        'ㅤㅤㅤㅤㅤㅤㅤ𝖻𝗎𝖾𝗇𝗈... 𝘱𝗎𝖽𝗈 𝗌𝖾𝗋 𝘱𝖾𝗈𝗋. \n'
        'ㅤㅤㅤ𝗌𝗈𝗅𝗈 𝖾𝗇𝖼𝗈𝗇𝗍𝗋𝖺𝗌𝗍𝖾 𝗍𝖾𝗅𝖺𝗋𝖺ñ𝖺𝗌, 𝗇𝗈 𝗌𝗎𝗆𝖺𝗌𝗍𝖾 \n'
        'ㅤㅤㅤㅤㅤㅤ       𝗇𝗂 𝗉𝖾𝗋𝖽𝗂𝗌𝗍𝖾 𝗇𝖺𝖽𝖺.'
    )

  bot.answer_callback_query(call.id)
  bot.edit_message_text(msg, call.message.chat.id, call.message.message_id)


# ==========================================
# === TIENDA DE POCIONES Y OBJETOS (/SHOP) ===
# ==========================================

@bot.message_handler(commands=["shop"])
def cmd_shop(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(message, "ㅤ⬚  necesitas un @username en Telegram.  ،͟,")
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  balance = db['users'][clean_user]['caramelos']

  text = (
      "ㅤ꒰ 🧛‍♂️ ꒱ㅤㅤ ㅤㅤㅤㅤ𝓥𝖺𝗆𝗉'𝗌 𝖲𝗁𝗈𝗉.\n\n"    
      f"Saldo actual: {balance} 🍬 \n\n"
      "𝖢𝗈𝗆𝗉𝗋𝖺 𝗈𝖻𝗃𝖾𝗍𝗈𝗌 𝗆á𝗀𝗂𝖼𝗈𝗌 𝗀𝖺𝗌𝗍𝖺𝗇𝖽𝗈 𝗍𝗎𝗌 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌:\n\n"
      "𖥻 `/buy veneno` (Costo: 250 ) ↝ 𝖤𝗅 𝗃𝗎𝗀𝖺𝖽𝗈𝗋 𝖺 𝗊𝗎𝗂é𝗇 𝖾𝗇𝗏𝖾𝗇𝖾𝗇𝖾𝗌 𝗇𝗈 𝗉𝗈𝖽𝗋á 𝗃𝗎𝗀𝖺𝗋 𝖽𝗎𝗋𝖺𝗇𝗍𝖾 𝟦 𝗁𝗈𝗋𝖺𝗌.\n"
      "𖥻 `/buy escudo` (Costo: 400 ) ↝ 𝖳𝖾 𝗉𝗋𝗈𝗍𝖾𝗀𝖾 𝖽𝖾 𝗆𝖺𝗅𝖽𝗂𝖼𝗂𝗈𝗇𝖾𝗌 𝗒 𝗏𝖾𝗇𝖾𝗇𝗈𝗌.\n"
      "𖥻 `/buy recompensa` (Costo: 500 ) ↝ 𝖳𝖾 𝗈𝗍𝗈𝗋𝗀𝖺 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌 𝖾𝗇𝗍𝗋𝖾 𝟧𝟢𝟢 𝗒 𝟣𝟢𝟢𝟢 𝗌𝖾𝗀ú𝗇 𝗅𝖺 𝗌𝗎𝖾𝗋𝗍𝖾.\n"
      "𖥻 `/buy milagrosa` (Costo: 100 ) ↝ 𝖰𝗎𝗂𝗍𝖺 𝖺𝗅𝖾𝖺𝗍𝗈𝗋𝗂𝖺𝗆𝖾𝗇𝗍𝖾 𝖾𝗇𝗍𝗋ེ་ 𝟢 y 𝟤𝟢𝟢 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌 a 𝗈𝗍𝗋𝗈 𝗎𝗌𝗎𝖺𝗋𝗂𝗈 𝗊𝗎𝖾 𝖾𝗅𝗂𝗃𝖺𝗌."
  )
  bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=["buy"])
def cmd_buy(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(message, "ㅤ⬚  necesitas un @username en Telegram.  ،͟,")
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  user_id = message.from_user.id
  args = message.text.lower().split()
  balance = db['users'][clean_user]['caramelos']

  if len(args) < 2:
    bot.reply_to(
        message,
        "❌ Indica qué objeto quieres comprar. Ejemplo: `/buy veneno`",
        parse_mode="Markdown",
    )
    return

  item = args[1]

  if item == "recompensa":
    cost = 500
    if balance < cost:
      bot.reply_to(message, "ㅤ⬚  no tienes suficientes caramelos (Costo: 500 ).  ،͟,")
      return
    db['users'][clean_user]['caramelos'] -= cost
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    premio = random.randint(500, 1000)
    db['users'][clean_user]['caramelos'] += premio
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    new_bal = db['users'][clean_user]['caramelos']
    bot.reply_to(
        message,
        f" ¡Has comprado la **recompensa mágica**!\nLa suerte ha decidido darte +{premio} caramelos (Saldo actual: {new_bal} 🍬)",
        parse_mode="Markdown",
    )

  elif item == "veneno":
    cost = 250
    if balance < cost:
      bot.reply_to(message, "ㅤ⬚  no tienes suficientes caramelos (Costo: 250 ).  ،͟,")
      return
    db['users'][clean_user]['caramelos'] -= cost
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0

    if user_id not in inventario:
      inventario[user_id] = {}
    inventario[user_id]["pocion_venenosa"] = inventario[user_id].get("pocion_venenosa", 0) + 1

    bot.reply_to(
        message,
        " ¡Has comprado una **poción venenosa**!\n Se ha guardado in tu inventario (`/items`).\n Para utilizarla usa `/envenenar @usuario`.",
        parse_mode="Markdown",
    )

  elif item == "escudo":
    cost = 400
    if balance < cost:
      bot.reply_to(message, "ㅤ⬚  no tienes suficientes caramelos (Costo: 400 ).  ،͟,")
      return
    db['users'][clean_user]['caramelos'] -= cost
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    if user_id not in inventario:
      inventario[user_id] = {}
    inventario[user_id]["escudo_activo"] = True
    bot.reply_to(
        message,
        " ¡Has comprado y activado un **escudo protector**!\nAhora eres inmune a las pociones venenosas.",
        parse_mode="Markdown",
    )

  elif item == "milagrosa":
    cost = 100
    if balance < cost:
      bot.reply_to(message, "ㅤ⬚  no tienes suficientes caramelos (Costo: 100 ).  ،͟,")
      return
    db['users'][clean_user]['caramelos'] -= cost
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    if user_id not in inventario:
      inventario[user_id] = {}
    inventario[user_id]["poción_milagrosa"] = inventario[user_id].get("poción_milagrosa", 0) + 1
    bot.reply_to(
        message,
        " ¡Has comprado una **poción milagrosa**!\n Usala respondiendo con `/milagrosa @usuario` para robar caramelos.",
        parse_mode="Markdown",
    )

  else:
    bot.reply_to(
        message,
        "❌ Esa poción no existe en la tienda. Revisa con `/shop`.",
    )


# ==========================================
# === COMANDOS DE POCIONES: ITEMS, ENVENEWAR Y MILAGROSA ===
# ==========================================

@bot.message_handler(commands=["items"])
def ver_inventario(message):
  user_id = message.from_user.id
  inv = inventario.get(user_id, {})
  veneno = inv.get("pocion_venenosa", 0)
  milagrosa = inv.get("poción_milagrosa", 0)
  escudo = "Sí 🛡️" if inv.get("escudo_activo") else "No"
  
  text = (
      f"🔮 **𝓘𝗍𝖾𝗆𝗌:**\n"
      f" 𖥻 Poción venenosa ↝ {veneno}\n"
      f" 𖥻 Poción milagrosa ↝ {milagrosa}\n"
      f" 𖥻 Escudo protector activo ↝ {escudo}"
  )
  bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=["envenenar"])
def envenenar_usuario(message):
  user_id = message.from_user.id

  if inventario.get(user_id, {}).get("pocion_venenosa", 0) <= 0:
    bot.reply_to(
        message,
        "❌ No tienes ninguna poción venenosa en tu inventario. ¡Compra una con /shop!",
    )
    return

  args = message.text.split()
  if len(args) < 2:
    bot.reply_to(
        message,
        "❌ Debes especificar a quién quieres envenenar usando `/envenenar @usuario`",
        parse_mode="Markdown",
    )
    return

  objetivo_username = sanitize_username(args[1])
  if not objetivo_username or objetivo_username not in db['users']:
    bot.reply_to(message, "❌ Usuario no encontrado o no registrado en el juego.")
    return

  objetivo_data = db['users'][objetivo_username]
  objetivo_id = objetivo_data.get('user_id')

  if objetivo_id and objetivo_id in inventario and inventario[objetivo_id].get("escudo_activo"):
    inventario[user_id]["pocion_venenosa"] -= 1
    bot.reply_to(
        message,
        f"🛡️ ¡@{objetivo_username} tiene un **escudo protector activo**! La poción venenosa rebotó y se ha perdido.",
        parse_mode="Markdown"
    )
    return

  inventario[user_id]["pocion_venenosa"] -= 1

  if objetivo_id:
    if objetivo_id not in inventario:
      inventario[objetivo_id] = {}
    inventario[objetivo_id]["veneno_until"] = datetime.datetime.now() + datetime.timedelta(hours=4)
  else:
    if 'poisoned_usernames' not in db:
      db['poisoned_usernames'] = {}
    db['poisoned_usernames'][objetivo_username] = datetime.datetime.now() + datetime.timedelta(hours=4)

  bot.reply_to(
      message, f"🧪 ¡Has utilizado una poción venenosa contra @{objetivo_username} que dura 4 horas!"
  )


@bot.message_handler(commands=["milagrosa"])
def milagrosa_usuario(message):
  user_id = message.from_user.id
  if inventario.get(user_id, {}).get("poción_milagrosa", 0) <= 0:
    return bot.reply_to(message, "❌ No tienes pociones milagrosas. ¡Cómprala en /shop!")

  args = message.text.split()
  if len(args) < 2:
    return bot.reply_to(message, "❌ Uso correcto: `/milagrosa @usuario`", parse_mode="Markdown")

  objetivo = sanitize_username(args[1])
  if objetivo not in db['users']:
    return bot.reply_to(message, "❌ El usuario objetivo no existe.")

  inventario[user_id]["poción_milagrosa"] -= 1
  robado = random.randint(0, 200)
  
  if db['users'][objetivo]['caramelos'] < robado:
    robado = db['users'][objetivo]['caramelos']

  db['users'][objetivo]['caramelos'] -= robado
  if db['users'][objetivo]['caramelos'] < 0:
    db['users'][objetivo]['caramelos'] = 0
    
  clean_user = sanitize_username(message.from_user.username)
  init_user(clean_user, message.from_user.id)
  db['users'][clean_user]['caramelos'] += robado
  if db['users'][clean_user]['caramelos'] < 0:
    db['users'][clean_user]['caramelos'] = 0

  bot.reply_to(message, f"✨ ¡La suerte está echada! La poción milagrosa le ha quitado {robado} caramelos a @{objetivo}.")


# ==========================================
# === JUEGO: OJOS (Botones sin dibujo de ojo) ===
# ==========================================

@bot.message_handler(commands=["ojos"])
def cmd_ojos(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(message, "ㅤ⬚  necesitas un @username en Telegram.  ،͟,")
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  args = message.text.split()
  if len(args) < 2 or not args[1].isdigit():
    bot.reply_to(
        message,
        "❌ Debes indicar una apuesta válida. Ejemplo: `/ojos 50`",
        parse_mode="Markdown",
    )
    return

  bet = int(args[1])
  if bet < 1:
    bot.reply_to(message, "❌ La apuesta mínima es de 1 caramelo.")
    return

  balance = db['users'][clean_user]['caramelos']
  if balance <= 0 or balance < bet:
    bot.reply_to(message, "ㅤ⬚  no tienes suficientes caramelos  ،͟,")
    return

  send_eye_game(message.chat.id, bet)


def send_eye_game(chat_id, bet, message_id=None):
  winning_pos = random.randint(0, 3)
  text = (
      "ㅤ꒰ 👁️ ꒱ ㅤㅤ ¿𝖼𝗎á𝗅 𝖾𝗌𝗍á 𝗆𝗂𝗋𝖺𝗇𝖽𝗈 𝖽𝗂𝗋𝖾𝖼𝗍𝖺𝗆𝖾𝗇𝗍𝖾?ㅤㅤㅤㅤㅤㅤㅤ\n"
      f"ㅤㅤㅤꞋꞌꞋꞌㅤㅤㅤㅤ𝖺𝗉𝗎𝖾𝗌𝗍𝖺: {bet} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈s. \n"
      "ㅤㅤㅤㅤ𝖼𝗎𝖺𝗍𝗋𝗈 𝗈𝗃𝗈𝗌 𝗍𝖾 𝗈𝖻𝗌𝖾𝗋𝗏𝖺𝗇 𝖾𝗇 𝗅𝖺 𝗈𝗌𝖼𝗎𝗋𝗂𝖽𝖺𝖽. ㅤㅤㅤㅤ\n"
      "ㅤ   ㅤ¡𝗁𝖺𝗓 𝖼𝗅𝗂𝖼 𝖾𝗇 𝖾𝗅 𝗊𝗎𝖾 𝗊𝗎𝖾𝗋𝗋𝖺𝗌 𝗊𝗎𝖾 𝗍𝖾 𝗆𝗂𝗋𝖺 𝖿𝗂𝗃𝖺𝗆𝖾𝗇𝗍𝖾!"
  )

  markup = InlineKeyboardMarkup(row_width=2)
  special_numbers = ["𝟏", "𝟐", "𝟑", "𝟒"]
  buttons = [
      InlineKeyboardButton(
          f"{special_numbers[i]}",
          callback_data=f"eye_{i}_{winning_pos}_{bet}",
      )
      for i in range(4)
  ]
  markup.add(*buttons)

  if message_id:
    bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
  else:
    bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('eye_'))
def handle_eye_callback(call):
  data_parts = call.data.split('_')
  chosen_pos = int(data_parts[1])
  winning_pos = int(data_parts[2])
  bet = int(data_parts[3])
  
  clicker = call.from_user.username
  clean_user = sanitize_username(clicker)
  init_user(clean_user, call.from_user.id)

  bot.answer_callback_query(call.id)
  
  acerto = (chosen_pos == winning_pos)
  
  if acerto:
    ganancia = bet * 2
    db['users'][clean_user]['caramelos'] += ganancia
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    text = (
        ' ㅤ꒰ 👁️ ꒱ ㅤㅤ ¡𝗁𝖺𝗌 𝖺𝖼𝖾𝗋𝗍𝖺𝖽𝗈! 𝖾𝗅 𝗈𝗃𝗈 #'
        f'{winning_pos + 1} 𝗍𝖾 𝗆𝗂𝗋𝖺𝟻𝖺.ㅤㅤㅤㅤㅤㅤ\n'
        ' ㅤ ㅤㅤ  ㅤ ㅤㅤ  '
        f'𝗀𝖺𝗇𝖺𝗌𝗍𝖾 {ganancia} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
    )
  else:
    db['users'][clean_user]['caramelos'] -= bet
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    text = (
        ' ㅤ꒰ 👁 ꒱ ㅤㅤ ¡𝗁𝖺𝗌 𝖿𝖺𝗅𝗅𝖺𝖽𝗈! 𝖾𝗅𝖾𝗀𝗂𝗌𝗍𝖾 𝖾𝗅 𝗈𝗃𝗈 ㅤㅤㅤㅤㅤㅤ\n'
        f'ㅤ𝗇ú𝗆𝖾𝗋𝗈 #{chosen_pos + 1}, 𝗉𝖾𝗋𝗈 𝖾𝗅 𝗊𝗎𝖾 𝗍𝖾 𝗆𝗂𝗋𝖺𝖻𝖺 𝖾𝗋𝖺 𝖾𝗅 𝗈𝗃𝗈 #'
        f'{winning_pos + 1}.\n'
        'ㅤㅤㅤㅤㅤㅤㅤ'
        f'𝗉𝖾𝗋𝖽𝗂𝗌𝗍𝖾 𝗍𝗎𝗌 {bet} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌.'
    )

  try:
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
  except Exception:
    pass


# ==========================================
# === JUEGO: SLOTWEEN (Con botón para girar) ===
# ==========================================

@bot.message_handler(commands=["slotween"])
def cmd_slotween(message):
  clicker = message.from_user.username
  if not clicker:
    return bot.reply_to(message, "ㅤ⬚  necesitas un @username en Telegram.  ،͟,")
  clean_user = sanitize_username(clicker)
  init_user(clean_user, message.from_user.id)

  if check_poisoned(message.from_user.id):
    return bot.reply_to(message, "❌ Estás envenenado y no puedes jugar. Solo puedes usar /cementerio.")

  args = message.text.split()
  if len(args) < 2 or not args[1].isdigit():
    bot.reply_to(
        message,
        "❌ Debes indicar una apuesta válida. Ejemplo: `/slotween 50`",
        parse_mode="Markdown",
    )
    return

  bet = int(args[1])
  if bet < 1:
    bot.reply_to(message, "❌ La apuesta mínima es de 1 caramelo.")
    return

  balance = db['users'][clean_user]['caramelos']
  if balance <= 0 or balance < bet:
    bot.reply_to(message, "ㅤ⬚  no tienes suficientes caramelos  ،͟,")
    return

  markup = InlineKeyboardMarkup()
  markup.add(InlineKeyboardButton("🎰 ¡Girar Máquina!", callback_data=f"spin_slot_{bet}_{clean_user}"))
  
  text = (
      "ㅤㅤ ⃟ ㅤㅤ𝓥𝖺𝗆𝗉'𝗌 𝗌𝗅𝗈𝗍 𝗆𝖺𝖼𝗁𝗂𝗇𝖾!ㅤㅤㅤㅤㅤㅤ\n\n"
      "ㅤㅤㅤㅤㅤㅤ ❓ | ❓ | ❓\n"
      "ㅤㅤㅤㅤㅤㅤ ❓ | ❓ | ❓\n"
      "ㅤㅤㅤㅤㅤㅤ ❓ | ❓ | ❓\n\n"
      f"ㅤㅤ𝖺𝗉𝗎𝖾𝗌𝗍𝖺: {bet} 𝖼𝖺𝗋𝖺𝗆𝖾𝗅𝗈𝗌. \n"
      "ㅤㅤ¡Presiona el botón para girar los carretes!"
  )
  bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('spin_slot_'))
def handle_slot_spin(call):
  parts = call.data.split('_')
  bet = int(parts[2])
  owner_user = parts[3]
  clean_clicker = sanitize_username(call.from_user.username)

  if clean_clicker != owner_user:
    return bot.answer_callback_query(call.id, "Esta máquina no es tuya.", show_alert=True)

  bot.answer_callback_query(call.id, "¡Girando carretes...")
  grid = [random.choices(SLOT_SYMBOLS, k=3) for _ in range(3)]
  
  ganancia = bet * 2
  won = False
  for row in grid:
    if row[0] == row[1] == row[2]:
      won = True
      break
  for col in range(3):
    if grid[0][col] == grid[1][col] == grid[2][col]:
      won = True
      break
  if grid[0][0] == grid[1][1] == grid[2][2]:
    won = True

  init_user(clean_clicker, call.from_user.id)
  if won:
    db['users'][clean_clicker]['caramelos'] += ganancia
    if db['users'][clean_clicker]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    resultado_txt = f"¡𝗏𝗂𝖼𝗍𝗈𝗋𝗂𝖺! Has ganado {ganancia} caramelos 🍬."
  else:
    db['users'][clean_clicker]['caramelos'] -= bet
    if db['users'][clean_user]['caramelos'] < 0:
      db['users'][clean_user]['caramelos'] = 0
    resultado_txt = f"No hubo suerte esta vez. Perdiste {bet} caramelos."

  text = (
      "ㅤㅤ ⃟ ㅤㅤ𝓥𝖺𝗆𝗉'𝗌 𝗌𝗅𝗈𝗍 𝗆𝖺𝖼𝗁𝗂𝗇𝖾!ㅤㅤㅤㅤㅤㅤ\n\n"
      f"ㅤㅤㅤㅤㅤㅤ {grid[0][0]} | {grid[0][1]} | {grid[0][2]}\n"
      f"ㅤㅤㅤㅤㅤㅤ {grid[1][0]} | {grid[1][1]} | {grid[1][2]}\n"
      f"ㅤㅤㅤㅤㅤㅤ {grid[2][0]} | {grid[2][1]} | {grid[2][2]}\n\n"
      f"ㅤㅤapuesta: {bet} caramelos.\n"
      f"ㅤㅤ{resultado_txt}"
  )
  try:
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id)
  except Exception:
    pass


bot.infinity_polling()
