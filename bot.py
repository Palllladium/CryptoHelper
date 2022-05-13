import requests
from datetime import datetime
import telebot
from auth_data import token
import re
from telebot import types
from yobitParser import get_orders_info_from_yobit, get_ticker_info_from_yobit
from poloniexParser import get_orders_info_from_poloniex, get_ticker_info_from_poloniex


def telegram_bot(token):
    bot = telebot.TeleBot(token)
    request = ""

    @bot.message_handler(commands=["help"])
    def help_message(message):
        bot.send_message(message.chat.id,
                         "Нажмите кнопку \"Price\" или напишите команду /price чтобы получить статистическую информацию"
                         " о торгах за последние 24 часа по паре монет, которая вас интересует\n"
                         "Обозначения - \n"
                         "High - максимальная цена\n"
                         "Low - минимальная цена\n"
                         "Avg - средняя цена\n"
                         "Vol - объем торгов\n"
                         "Last - цена последней сделки\n"
                         "Buy - цена покупки\n"
                         "Sell - цена продажи\n\n"
                         "Нажмите \"Orders\" или напишите команду /orders чтобы получить информацию о наиболее выгодных"
                         " актуальных предложениях на покупку/продажу интересущей вас пары монет")

    @bot.message_handler(commands=["price", "orders"])
    def command_message(message):
        nonlocal request
        request = ""
        request += f"{message.text[1:]} "
        bot.send_message(message.chat.id, 'Введите пару монет, по которой хотите получить информацию\n'
                                          'Пример: btc to usdt')

    @bot.message_handler(commands=["start"])
    def start_message(message):
        """markip_inline = types.InlineKeyboardMarkup()
        item_price = types.InlineKeyboardButton(text='Price', callback_data='Price ')
        item_orders = types.InlineKeyboardButton(text='Orders', callback_data='Orders ')
        markip_inline.add(item_price, item_orders)
        bot.send_message(message.chat.id, "Hello friend! Write the 'price' to find out the cost of BTC!",
                         reply_markup=markip_inline)"""
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_price = types.KeyboardButton('/price')
        item_orders = types.KeyboardButton('/orders')
        markup_reply.add(item_price, item_orders)
        bot.send_message(message.chat.id, "Привет, если хочешь узнать, что я умею, введи команду /help",
                         reply_markup=markup_reply)

    @bot.callback_query_handler(func=lambda call: True)
    def answer_of_call(call):
        nonlocal request
        request = ""
        request += call.data
        bot.send_message(call.message.chat.id, 'Enter pair of coins like this: btc to usd')

    regex_of_ticker_yobit = re.compile("price[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z]{2,6}[\s]*")
    regex_of_ticker_poloniex = re.compile("2price[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z]{2,6}[\s]*")
    regex_of_depth_yobit = re.compile("orders[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z\s]{2,6}[\s]*")
    regex_of_depth_poloniex = re.compile("2orders[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z\s]{2,6}[\s]*")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        nonlocal request
        request += message.text
        answer = {
            regex_of_depth_yobit.match(request.lower()): get_orders_info_from_yobit(request),
            regex_of_depth_poloniex.match(request.lower()): get_orders_info_from_poloniex(request),
            regex_of_ticker_poloniex.match(request.lower()): get_ticker_info_from_poloniex(request),
            regex_of_ticker_yobit.match(request.lower()): get_ticker_info_from_yobit(request),
            True: "Чтооо??? Я тебя не понимаю, попробуй ввести другую команду!"
        }

        # current orders
        if regex_of_depth_yobit.match(request.lower()):

            try:
                names_of_coins = request.lower()[6:].split(" to ")
                req = requests.get(f"https://yobit.net/api/3/depth/"
                                   f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}"
                                   f"?limit={5}&ignore_invalid=1")
                response = req.json()
                info_of_orders = response[f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}"]
                items = ["asks", "bids"]
                answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                         f"Наиболее выгодные предложения по паре" \
                         f" {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n"

                for item in items:
                    array_of_orders = info_of_orders[item]
                    map = {"asks": "Покупка", "bids": "Продажа"}
                    answer += f"\n{map[item]}:\n"
                    for order in array_of_orders:
                        answer += f"Цена: {order[0]},   Объем: {order[1]}\n"

                bot.send_message(
                    message.chat.id,
                    answer
                )

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Оооу... Что-то пошло не так, возможно, данная пара не торгуется на выбранной вами бирже,"
                    " попробуйте снова:("
                )
                request = ""

        elif regex_of_depth_poloniex.match(request.lower()):
            try:
                names_of_coins = request[7:].split(" to ")
                req = requests.get(f"https://poloniex.com/public?command=returnOrderBook&currencyPair="
                                   f"{names_of_coins[1].strip().upper()}_{names_of_coins[0].strip().upper()}&depth=5")
                response = req.json()
                info_of_orders = response
                items = ["asks", "bids"]
                answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                         f"Наиболее выгодные предложения по паре" \
                         f" {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n"
                for item in items:
                    array_of_orders = info_of_orders[item]
                    map = {"asks": "Покупка", "bids": "Продажа"}
                    answer += f"\n{map[item]}:\n"
                    for order in array_of_orders:
                        answer += f"Цена: {order[0]},   Объем: {order[1]}\n"

                bot.send_message(
                    message.chat.id,
                    answer
                )

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Оооу... Что-то пошло не так, возможно, данная пара не торгуется на выбранной вами бирже,"
                    " попробуйте снова:("
                )
                request = ""

        elif regex_of_ticker_poloniex.match(request.lower()):
            try:
                names_of_coins = request[7:].split(" to ")
                req = requests.get("https://poloniex.com/public?command=returnTicker")
                response = req.json()
                info_of_ticker = response[f"{names_of_coins[1].strip().upper()}_{names_of_coins[0].strip().upper()}"]
                items = ["last", "low24hr", "high24hr", "percentChange"]
                answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                         f"Информация по паре {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n\n"
                for item in items:
                    answer += f"{item}: {info_of_ticker[item]}\n"

                bot.send_message(
                    message.chat.id,
                    answer
                )

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Оооу... Что-то пошло не так, возможно, данная пара не торгуется на выбранной вами бирже,"
                    " попробуйте снова:("
                )
                request = ""

        elif regex_of_ticker_yobit.match(request.lower()):
            try:
                names_of_coins = request.lower()[6:].split(" to ")
                req = requests.get(f"https://yobit.net/api/3/ticker/"
                                   f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}")
                response = req.json()
                info_of_ticker = response[f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}"]
                items = ["High", "Low", "Avg", "Vol", "Last", "Buy", "Sell"]
                answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                         f"Информация по паре {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n\n"
                for item in items:
                    answer += f"{item}: {info_of_ticker[item.lower()]}\n"

                """bot.send_message(
                    message.chat.id,
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n "
                    f"Sell {names_of_coins[0]} to {names_of_coins[1]} price: {sell_price}"
                )"""

                bot.send_message(
                    message.chat.id,
                    answer
                )

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Оооу... Что-то пошло не так, возможно, данная пара не торгуется на выбранной вами бирже,"
                    " попробуйте снова:("
                )
                request = ""

        else:
            bot.send_message(message.chat.id, "Чтооо??? Я тебя не понимаю, попробуй ввести другую команду!")
        request = ""

    bot.polling()


if __name__ == '__main__':
    print('KAKZHEYAZAEBALSYA')
    telegram_bot(token)
