from flask import Flask
from threading import Thread
import os
import time

# Импортируем ТВОЙ файл с ботом
# Предполагается, что твой бот запускается функцией bot.infinity_polling()
import bot  

app = Flask(__name__)

# Простой веб-сервер, чтобы Render видел, что приложение запущено
@app.route('/')
def home():
    return "Бот работает!"

@app.route('/health')
def health():
    return "OK"

# Функция, которая запускает твоего бота в отдельном потоке
def run_bot():
    # Здесь твой код запуска, как в bot.py
    # Например: bot.bot.infinity_polling()
    bot.bot.infinity_polling() 

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    thread = Thread(target=run_bot)
    thread.start()
    
    # Запускаем Flask-сервер, который будет слушать порт от Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
