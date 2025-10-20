import os
import telebot
import requests
import threading
from flask import Flask

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

print("=== BOT STARTING ===")
print(f"BOT_TOKEN: {'*' * 10}{BOT_TOKEN[-5:] if BOT_TOKEN else 'NOT SET'}")
print(f"WEATHER_API_KEY: {'*' * 10}{WEATHER_API_KEY[-5:] if WEATHER_API_KEY else 'NOT SET'}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"📨 Received /start from {message.chat.id}")
    bot.reply_to(message, "Привет! Я бот погоды. Напиши название города, чтобы я мог рассказать тебе о погоде.")

@bot.message_handler(func=lambda message: True)
def send_weather(message):
    try:
        print(f"📨 Received: '{message.text}' from {message.chat.id}")
        city = message.text.strip()
        
        if not city:
            bot.reply_to(message, "Пожалуйста, введите название города.")
            return
            
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        print(f"🌐 Fetching weather for: {city}")
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        print(f"🌤️ API Response: {data.get('cod')}")
        
        if data.get('cod') == 200:
            weather_info = f"""
🌍 Город: {data['name']}
🌡️ Температура: {data['main']['temp']}°C
💨 Ощущается как: {data['main']['feels_like']}°C
📝 Описание: {data['weather'][0]['description']}
💧 Влажность: {data['main']['humidity']}%
🌬️ Ветер: {data['wind']['speed']} м/с
"""
            bot.reply_to(message, weather_info)
            print("✅ Weather sent successfully")
        else:
            error_msg = data.get('message', 'Unknown error')
            print(f"❌ API Error: {error_msg}")
            bot.reply_to(message, f"❌ Город '{city}' не найден. Проверьте название.")
            
    except requests.exceptions.Timeout:
        print("❌ API Timeout")
        bot.reply_to(message, "⏰ Таймаут запроса. Попробуйте позже.")
    except Exception as e:
        print(f"❌ Error: {e}")
        bot.reply_to(message, "⚠️ Произошла ошибка. Попробуйте позже.")

@app.route('/')
def index():
    return "🤖 Bot is running! Use Telegram to interact with the bot."

def start_bot_polling():
    print("🔄 Starting bot polling...")
    try:
        bot.remove_webhook()
        print("✅ Webhook removed")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Polling error: {e}")

if __name__ == "__main__":
    print("🚀 Starting application...")
    
    bot_thread = threading.Thread(target=start_bot_polling)
    bot_thread.daemon = True
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Starting Flask on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)


