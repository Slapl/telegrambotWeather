import os
import telebot
import requests
from flask import Flask

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

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
        print(f"Error: {e}")

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ.get('RAILWAY_STATIC_URL')}.railway.app/" + BOT_TOKEN)
    return "Bot is running!", 200

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))