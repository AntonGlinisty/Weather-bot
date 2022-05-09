import telebot
from telebot import types
import requests
import datetime
from config import token, open_weather_token

bot = telebot.TeleBot(token)
lat = 0
lon = 0

@bot.message_handler(commands=["start"])
def start_command(message):
    markup = markmainmenu()
    bot.send_message(message.chat.id, "Привет! Прямо сейчас вы сможете узнать погоду в любой точке мира!!! ", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def bot_message(message):
    print(message)
    print(message.text)
    if message.text == '🌥 Погода':
        messweth(message)
    elif message.text == '📋 Информация':
        messinfo(message)
    elif message.text == 'Погода по широте и долготе':
        messlat(message)
    elif message.text == 'Погода в конкретном городе':
        messcity(message)
    elif message.text == '⬅ Назад':
        messback(message)
    else:
        messunknown(message)

def messweth(message):
    markup = markmainweath()
    bot.send_message(message.chat.id, '🌥 Погода', reply_markup=markup)

def messinfo(message):
    text = info()
    bot.send_message(message.chat.id, text)

def messlat(message):
    markup = markback()
    bot.send_message(message.chat.id, 'Введите широту: ', reply_markup=markup)
    bot.register_next_step_handler(message, lat_input)

def messcity(message):
    markup = markback()
    bot.send_message(message.chat.id, 'Введите город: ', reply_markup=markup)
    bot.register_next_step_handler(message, city_input)

def messback(message):
    markup = markmainmenu()
    bot.send_message(message.chat.id, '⬅ Назад', reply_markup=markup)

def messunknown(message):
    bot.send_message(message.chat.id, 'Нераспознанная команда')

def markmainmenu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('🌥 Погода')
    item2 = types.KeyboardButton('📋 Информация')
    markup.add(item1, item2)
    return markup

def markmainweath():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Погода по широте и долготе')
    item2 = types.KeyboardButton('Погода в конкретном городе')
    item3 = types.KeyboardButton('⬅ Назад')
    markup.add(item1, item2, item3)
    return markup

def markback():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('⬅ Назад')
    markup.add(item1)
    return markup

def info():
    text = ''
    with open('info.txt', 'r', encoding='utf_8') as file:
        for lines in file.readlines():
            text += lines
    return text

def emojes():
    smiles = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }
    return smiles

def weatheroutput(data, message, smiles):
    cur_weather = data["main"]["temp"]
    weather_description = data["weather"][0]["main"]
    if weather_description in smiles:
        wd = smiles[weather_description]
    else:
        wd = "Посмотрите в окно, не пойму что там за погода!"
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind = data["wind"]["speed"]
    sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
    sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
    length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
        data["sys"]["sunrise"])
    markup = markmainmenu()
    bot.send_message(message.chat.id, f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n\n"
                                      f"Температура: {cur_weather}C° {wd}\nВлажность: {humidity}%\n"
                                      f"Давление: {pressure} мм.рт.ст\n"
                                      f"Скорость ветра: {wind} м/с\nВосход солнца: {sunrise_timestamp}\n"
                                      f"Закат солнца: {sunset_timestamp}\n"
                                      f"Продолжительность дня: {length_of_the_day}\n\n***Одевайтесь по погоде!***",
                     reply_markup=markup)

@bot.message_handler()
def lat_input(message):
    try:
        int(message.text)
        if -90 <= int(message.text) <= 90:
            global lat
            lat = message.text
            bot.send_message(message.chat.id, "Теперь введите долготу: ")
            bot.register_next_step_handler(message, lon_input)
        else:
            if message.text == '⬅ Назад':
                message.text = '🌥 Погода'
                bot_message(message)
            else:
                bot.send_message(message.chat.id, "Широта изменяется в пределах [-90, 90]\nВведите широту: ")
                bot.register_next_step_handler(message, lat_input)
    except:
        if message.text == '⬅ Назад':
            message.text = '🌥 Погода'
            bot_message(message)
        else:
            bot.send_message(message.chat.id, "Введите корректное число: ")
            bot.register_next_step_handler(message, lat_input)

@bot.message_handler()
def lon_input(message):
    try:
        int(message.text)
        if -180 <= int(message.text) <= 180:
            global lon
            lon = message.text
            result(message)
        else:
            if message.text == '⬅ Назад':
                message.text = 'Погода по широте и долготе'
                bot_message(message)
            else:
                bot.send_message(message.chat.id, "Долгота изменяется в пределах [-180, 180]\nВведите долготу: ")
                bot.register_next_step_handler(message, lon_input)
    except:
        if message.text == '⬅ Назад':
            message.text = 'Погода по широте и долготе'
            bot_message(message)
        else:
            bot.send_message(message.chat.id, "Введите корректное число: ")
            bot.register_next_step_handler(message, lon_input)

@bot.message_handler()
def city_input(message):
    try:
        global lat, lon
        r = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={message.text}"
                         f"&limit=1&appid={open_weather_token}")
        data = r.json()
        lat = data[0]["lat"]
        lon = data[0]["lon"]
        result(message)
    except:
        if message.text == '⬅ Назад':
            message.text = '🌥 Погода'
            bot_message(message)
        else:
            bot.send_message(message.chat.id, "Введите корректное название города: ")
            bot.register_next_step_handler(message, city_input)

def result(message):
    smiles = emojes()
    try:
        global lat, lon
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}"
            f"&lon={lon}&appid={open_weather_token}&units=metric"
        )
        data = r.json()
        weatheroutput(data, message, smiles)
    except:
        bot.send_message(message.chat.id, "\U00002620 Проверьте корректность введенных данных \U00002620")

bot.polling(none_stop=True)