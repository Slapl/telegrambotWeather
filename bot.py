import os
import telebot
import requests
from flask import Flask, request
import logging

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

if not BOT_TOKEN or not WEATHER_API_KEY:
    logging.error("Missing BOT_TOKEN or WEATHER_API_KEY environment variables")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот погоды. Напиши название города, и я покажу погоду.")

@bot.message_handler(func=lambda message: True)
def send_weather(message):
    try:
        city = message.text
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        
        response = requests.get(url)
        data = response.json()
        
        if data['cod'] == 200:
            weather_info = f"""
🌍 Город: {data['name']}
🌡️ Температура: {data['main']['temp']}°C
💨 Ощущается как: {data['main']['feels_like']}°C
📝 Описание: {data['weather'][0]['description']}
💧 Влажность: {data['main']['humidity']}%
🌬️ Ветер: {data['wind']['speed']} м/с
            """
            bot.reply_to(message, weather_info)
        else:
            bot.reply_to(message, "❌ Город не найден. Проверьте название и попробуйте снова.")
            
    except Exception as e:
        bot.reply_to(message, "⚠️ Произошла ошибка. Попробуйте позже.")
        logging.error(f"Weather error: {e}")

@app.route('/')
def index():
    return "Bot is running!", 200

@app.route('/webhook/' + BOT_TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Bad request', 400


@app.before_first_request
def set_webhook():
    webhook_url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'your-app-name')}.railway.app/webhook/{BOT_TOKEN}"
    try:
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        logging.info(f"Webhook set to: {webhook_url}")
    except Exception as e:
        logging.error(f"Webhook setup error: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
