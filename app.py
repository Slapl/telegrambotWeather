import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
URL = os.environ.get("RENDER_EXTERNAL_URL")  

bot = telebot.TeleBot(TOKEN, threaded=False)  
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот, который работает на Render.com")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, f"Ты написал: {message.text}")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def healthcheck():
    return 'Bot is running', 200
  
@app.route('/set_webhook')
def set_webhook():
    webhook_url = f'{URL}/{TOKEN}'
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f'Webhook set to {webhook_url}', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
