import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import datetime
import time

TOKEN = "8853154935:AAFx0EFcrrUPAI0UWtlcxGgE0eCSSh3TyTA"  # ЗАМЕНИ

# ===== РАЗДЕЛЕНИЕ РОЛЕЙ =====
ADMIN_ID = 5457874590  # ID твоего ОСНОВНОГО аккаунта (ЗАМЕНИ)
SUPPORT_ID = 8480606059  # ID твоего ТВИНКА @wiwiwewi (ЗАМЕНИ)

bot = telebot.TeleBot(TOKEN)

# ===== БАЗА ДАННЫХ =====
def init_db():
    conn = sqlite3.connect('ankets.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS ankets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        nickname TEXT,
        build TEXT,
        purpose TEXT,
        experience TEXT,
        experience_desc TEXT,
        tg_contact TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

# ===== ХРАНИЛИЩЕ =====
user_data = {}

def get_state(user_id):
    return user_data.get(user_id, {})

def set_state(user_id, key, value):
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value

def clear_state(user_id):
    if user_id in user_data:
        del user_data[user_id]

def save_anket(user_id, nickname, build, purpose, experience, experience_desc, tg_contact):
    conn = sqlite3.connect('ankets.db')
    cur = conn.cursor()
    cur.execute('''INSERT INTO ankets 
        (user_id, nickname, build, purpose, experience, experience_desc, tg_contact)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (user_id, nickname, build, purpose, experience, experience_desc, tg_contact))
    conn.commit()
    conn.close()

# ===== КЛАВИАТУРЫ =====
def main_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ Да", callback_data="start_anket"),
        InlineKeyboardButton("❌ Нет", callback_data="no_main"),
        InlineKeyboardButton("🆘 Поддержка", callback_data="support")
    )
    return keyboard

def yes_no_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ Да", callback_data="yes"),
        InlineKeyboardButton("❌ Нет", callback_data="no")
    )
    return keyboard

# ===== ОТПРАВКА АНКЕТЫ =====
def send_anket_to_admin(user_id, nickname, build, purpose, experience, experience_desc, tg_contact):
    text = f"""📋 **НОВАЯ АНКЕТА!**

👤 **Никнейм:** {nickname}
📦 **Сборка:** {'✅ Скачал' if build == 'yes' else '❌ Не скачал'}

🎯 **Чем хочет заняться:**
{purpose}

📚 **Опыт:** {'✅ Был' if experience == 'yes' else '❌ Не было'}
{f'📝 **Чем занимался:** {experience_desc}' if experience == 'yes' and experience_desc else ''}

📱 **Telegram:** {tg_contact}

🕐 **Время:** {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
    
    try:
        bot.send_message(ADMIN_ID, text, parse_mode='Markdown')
        print(f"✅ Анкета отправлена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# ===== ОБРАБОТЧИКИ =====

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    clear_state(user_id)
    
    bot.send_message(
        message.chat.id,
        "Приветствую! Вы в боте для создания анкет для проекта 'qwiwi'. Хотите создать анкету?",
        reply_markup=main_menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    step = get_state(user_id).get('step')
    
    # ===== ГЛАВНОЕ МЕНЮ =====
    if data == "start_anket":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Отлично! Напишите ваш игровой никнейм.")
        set_state(user_id, 'step', 'nickname')
    
    elif data == "no_main":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Жаль( Но в любой момент вы можете вернуться к нам <3")
    
    elif data == "support":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "Что-то случилось? Пишите сюда - @wiwiwewi"
        )
        try:
            bot.send_message(
                SUPPORT_ID,
                f"🆘 Пользователь запросил поддержку!"
            )
        except:
            pass
    
    # ===== ВОПРОС О СБОРКЕ =====
    elif data == "yes" and step == 'build':
        set_state(user_id, 'build', 'yes')
        bot.edit_message_text(
            "Хорошо, теперь опишите чем бы вы хотели заняться на нашем сервере!",
            call.message.chat.id,
            call.message.message_id
        )
        set_state(user_id, 'step', 'purpose')
    
    elif data == "no" and step == 'build':
        set_state(user_id, 'build', 'no')
        bot.edit_message_text(
            "❌ Вы не скачали сборку.\n\n📥 Скачайте её в нашем Discord:\n🔗 https://discord.gg/nBgHFUBDVy\n\n✅ Когда скачаете - просто напишите 'Готово' и продолжим!",
            call.message.chat.id,
            call.message.message_id
        )
        set_state(user_id, 'step', 'waiting_for_build')
    
    # ===== ВОПРОС ОБ ОПЫТЕ =====
    elif data == "yes" and step == 'experience':
        set_state(user_id, 'experience', 'yes')
        bot.edit_message_text(
            "Чем вы там занимались?",
            call.message.chat.id,
            call.message.message_id
        )
        set_state(user_id, 'step', 'experience_desc')
    
    elif data == "no" and step == 'experience':
        set_state(user_id, 'experience', 'no')
        bot.edit_message_text(
            "Мы рады быть вашим первым проектом такого формата! <3",
            call.message.chat.id,
            call.message.message_id
        )
        bot.send_message(
            call.message.chat.id,
            "Напишите свой Telegram @username для обратной связи"
        )
        set_state(user_id, 'step', 'tg_contact')
    
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    state = get_state(user_id)
    step = state.get('step')
    
    if not step:
        bot.send_message(
            message.chat.id,
            "Нажмите /start чтобы начать создание анкеты"
        )
        return
    
    if step == 'nickname':
        set_state(user_id, 'nickname', text)
        set_state(user_id, 'step', 'build')
        bot.send_message(
            message.chat.id,
            "Вы скачали сборку?",
            reply_markup=yes_no_menu()
        )
    
    elif step == 'purpose':
        set_state(user_id, 'purpose', text)
        set_state(user_id, 'step', 'experience')
        bot.send_message(
            message.chat.id,
            "Был ли у вас опыт на подобных серверах?",
            reply_markup=yes_no_menu()
        )
    
    elif step == 'experience_desc':
        set_state(user_id, 'experience_desc', text)
        set_state(user_id, 'step', 'tg_contact')
        bot.send_message(
            message.chat.id,
            "Напишите свой Telegram @username для обратной связи"
        )
    
    elif step == 'tg_contact':
        if not text.startswith('@'):
            bot.send_message(
                message.chat.id,
                "Пожалуйста, введите юзернейм с @, например: @username"
            )
            return
        
        set_state(user_id, 'tg_contact', text)
        data = get_state(user_id)
        
        save_anket(
            user_id,
            data.get('nickname'),
            data.get('build'),
            data.get('purpose'),
            data.get('experience'),
            data.get('experience_desc'),
            text
        )
        
        send_anket_to_admin(
            user_id,
            data.get('nickname'),
            data.get('build'),
            data.get('purpose'),
            data.get('experience'),
            data.get('experience_desc'),
            text
        )
        
        bot.send_message(
            message.chat.id,
            "✅ Отлично, ожидайте одобрения, с вами свяжутся!"
        )
        clear_state(user_id)
    
    # ===== ОЖИДАНИЕ СБОРКИ =====
    elif step == 'waiting_for_build':
        if text.lower() in ['готово', 'да', '+', 'скачал', 'yes', 'ок', 'окей', 'скачал сборку']:
            set_state(user_id, 'step', 'purpose')
            bot.send_message(
                message.chat.id,
                "Отлично! Теперь опишите чем бы вы хотели заняться на нашем сервере!"
            )
        else:
            bot.send_message(
                message.chat.id,
                "📥 Напомню: скачайте сборку в Discord:\n🔗 https://discord.gg/qwiwi\n\nКогда скачаете - напишите 'Готово'"
            )

def safe_polling():
    while True:
        try:
            print("🤖 Бот запущен!")
            print(f"📨 Анкеты приходят на ID: {ADMIN_ID}")
            print(f"🆘 Поддержка направляется на ID: {SUPPORT_ID} (@wiwiwewi)")
            bot.infinity_polling()
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)

if __name__ == "__main__":
    print("🚀 Запуск бота для Minecraft сервера 'qwiwi'")
    safe_polling()
