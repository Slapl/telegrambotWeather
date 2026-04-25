import os
import requests
from flask import Flask, request
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")  # Ключ от OpenWeatherMap или другого сервиса
URL = os.environ.get("RENDER_EXTERNAL_URL")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

def get_weather(city):
    """Запрос погоды — подставь свой API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("cod") != 200:
            return f"Город '{city}' не найден. Попробуй еще раз."

        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        description = data['weather'][0]['description']
        return (f"🌍 Погода в {city}:\n"
                f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                f"☁️ {description.capitalize()}")
    except Exception as e:
        return " Ошибка получения данных. Попробуй позже."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Напиши название города, и я скажу погоду ☀️")

@bot.message_handler(func=lambda message: True)
def weather_reply(message):
    city = message.text.strip()
    bot.reply_to(message, get_weather(city))

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def healthcheck():
    return 'Weather bot is running', 200

@app.route('/set_webhook')
def set_webhook():
    webhook_url = f'{URL}/{TOKEN}'
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f'Webhook set to {webhook_url}', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
