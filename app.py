from flask import Flask
from threading import Thread
import os
import bot
import logging
import traceback

# Настройка логирования для отлова ошибок
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

@app.route('/health')
def health():
    # Проверка, жив ли бот (можно добавить проверку статуса)
    return "OK", 200

def run_bot():
    try:
        logging.info("Запуск телеграм-бота...")
        # Убедись, что объект бота доступен как bot.bot или bot.application
        bot.bot.infinity_polling()
    except Exception as e:
        logging.error(f"Ошибка в телеграм-боте: {e}")
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    thread = Thread(target=run_bot)
    thread.start()
    logging.info("Flask-сервер запущен!")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
