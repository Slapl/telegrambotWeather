import telebot
import requests
import os
import logging
from background import keep_alive

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY', '')

if not TELEGRAM_BOT_TOKEN or not OPENWEATHERMAP_API_KEY:
    raise ValueError('❌ Необходимо установить TELEGRAM_BOT_TOKEN и OPENWEATHERMAP_API_KEY в переменных окружения')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

start_txt = 'Привет! Это бот прогноза погоды. \n\nОтправьте боту название города и он скажет, какая там температура и как она ощущается.'


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, start_txt, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def weather(message):
    city = message.text
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={OPENWEATHERMAP_API_KEY}'
    
    try:
        response = requests.get(url, timeout=10)
        weather_data = response.json()
        
        cod = str(weather_data.get('cod'))
        logger.debug(f'API response code: {cod}, status: {response.status_code}')
        
        if cod == '401':
            logger.error('Ошибка авторизации API OpenWeatherMap')
            bot.send_message(message.from_user.id, '❌ Ошибка конфигурации бота. Обратитесь к администратору.')
            return
        
        if cod == '404':
            logger.info(f'Город не найден: {city}')
            bot.send_message(message.from_user.id, f'❌ Город "{city}" не найден. Попробуйте еще раз.')
            return
        
        if cod != '200':
            logger.warning(f'Неожиданный ответ API: {cod} - {weather_data.get("message")}')
            bot.send_message(message.from_user.id, '❌ Произошла ошибка при получении данных о погоде. Попробуйте позже.')
            return
        
        temperature = round(weather_data['main']['temp'])
        temperature_feels = round(weather_data['main']['feels_like'])
        w_now = f'Сейчас в городе {city} {temperature} °C'
        w_feels = f'Ощущается как {temperature_feels} °C'
        
        logger.info(f'Погода отправлена для города: {city}')
        bot.send_message(message.from_user.id, w_now)
        bot.send_message(message.from_user.id, w_feels)
        
    except requests.exceptions.Timeout:
        logger.error(f'Превышено время ожидания запроса для города: {city}')
        bot.send_message(message.from_user.id, '❌ Превышено время ожидания. Попробуйте позже.')
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка сети при запросе погоды: {e}')
        bot.send_message(message.from_user.id, '❌ Ошибка соединения. Проверьте подключение к интернету.')
    except Exception as e:
        logger.exception(f'Неожиданная ошибка при получении погоды: {e}')
        bot.send_message(message.from_user.id, '❌ Произошла ошибка при получении данных о погоде. Попробуйте позже.')


if __name__ == '__main__':
    import time
    keep_alive()
    logger.info('🤖 Бот запущен и готов к работе!')
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            logger.error(f'❌ Ошибка: {e}')
            logger.info('🔄 Перезапуск бота через 5 секунд...')
            time.sleep(5)
