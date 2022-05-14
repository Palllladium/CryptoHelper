import telebot
from auth_data import token
import re
from telebot import types
from yobitParser import get_orders_info_from_yobit, get_ticker_info_from_yobit
from poloniexParser import get_orders_info_from_poloniex, get_ticker_info_from_poloniex
from binanceParser import get_orders_info_from_binance, get_ticker_info_from_binance
import time

def timer_subscribe():
    while True:
        print('kek')
        time.sleep(5)


def telegram_bot(token):
    bot = telebot.TeleBot(token)
    request = ""
    current_exchange = ""
    is_subscribe = False

    def timer_subscribe():
        """while is_subscribe:
            change = get_change()
            if change>5:
                bot.send_message()
            time.sleep(5)"""
        pass

    @bot.message_handler(commands=["subscribe"])
    def subscribe(message):
        bot.send_message(message.chat.id, "Чтобы получать сообщения об изменениях цены на пару, напиши с какой биржи"
                                          " хочешь получать информацию, о какой паре и об изменении на сколько "
                                          "процентов тебя стоит уведомлять\n"
                                          "Пример:\n"
                                          "Subscribe: Binance, btc to usdt, 10")

    @bot.message_handler(commands=["unsubscribe"])
    def subscribe(message):
        nonlocal is_subscribe
        is_subscribe = False
        bot.send_message(message.chat.id, "Ты описался от всех оповещений")

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

    @bot.message_handler(commands=["exchange"])
    def choose_exchange(message):
        markup_inline = types.InlineKeyboardMarkup()
        item_poloniex = types.InlineKeyboardButton(text='Poloniex', callback_data='Poloniex')
        item_yobit = types.InlineKeyboardButton(text='Yobit', callback_data='Yobit')
        item_binance = types.InlineKeyboardButton(text='Binance', callback_data='Binance')
        markup_inline.add(item_poloniex, item_yobit, item_binance)
        bot.send_message(message.chat.id, "Выбери биржу, с которой хочешь получать инфомацию\n"
                                          "Позже ты сможешь изменить это позже с помощью команды /exchange",
                         reply_markup=markup_inline)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        markup_inline = types.InlineKeyboardMarkup()
        item_poloniex = types.InlineKeyboardButton(text='Poloniex', callback_data='Poloniex')
        item_yobit = types.InlineKeyboardButton(text='Yobit', callback_data='Yobit')
        item_binance = types.InlineKeyboardButton(text='Binance', callback_data='Binance')
        markup_inline.add(item_poloniex, item_yobit, item_binance)
        bot.send_message(message.chat.id, "Привет, если хочешь узнать, что я умею, введи команду /help")
        bot.send_message(message.chat.id, "Выбери биржу, с которой хочешь получать инфомацию\n"
                                          "Позже ты сможешь изменить это позже с помощью команды /chooseExchange",
                         reply_markup=markup_inline)

    @bot.callback_query_handler(func=lambda call: True)
    def answer_of_call(call):
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_price = types.KeyboardButton('/price')
        item_orders = types.KeyboardButton('/orders')
        markup_reply.add(item_price, item_orders)
        bot.send_message(call.message.chat.id, f"Отлично, ты выбрал биржу {call.data}\n"
                                               f"Теперь выбери, что ты хочешь узнать: информацию о паре или актуальные"
                                               f" предложения покупки/продажи",
                         reply_markup=markup_reply
                         )
        nonlocal current_exchange
        current_exchange = call.data

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        regex_of_subscribe = re.compile("Subscribe: [a-zA-Z]+")
        if regex_of_subscribe.match(message.text):
            data = f"{message.chat.id} {' '.join(message.text[11:].split(', '))}\n"
            print(data)
            f = open('dataSubscribe.txt', 'a')
            f.write(data)
            f.close()
            bot.send_message(message.chat.id, "Отлично, подписка выполнена")
            nonlocal is_subscribe
            is_subscribe = True
            timer_subscribe()
            return

        nonlocal request
        nonlocal current_exchange
        request += message.text
        regex_of_ticker = re.compile("price[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z]{2,6}[\s]*")
        regex_of_depth = re.compile("orders[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z\s]{2,6}[\s]*")
        if current_exchange == "Poloniex":
            if regex_of_depth.match(request.lower()):
                answer = get_orders_info_from_poloniex(request)
            elif regex_of_ticker.match(request.lower()):
                answer = get_ticker_info_from_poloniex(request)
            else:
                answer = "Чтооо??? Я тебя не понимаю, попробуй ввести другую команду!"
        elif current_exchange == "Yobit":
            if regex_of_depth.match(request.lower()):
                answer = get_orders_info_from_yobit(request)
            elif regex_of_ticker.match(request.lower()):
                answer = get_ticker_info_from_yobit(request)
            else:
                answer = "Чтооо??? Я тебя не понимаю, попробуй ввести другую команду!"
        elif current_exchange == "Binance":
            if regex_of_depth.match(request.lower()):
                answer = get_orders_info_from_binance(request)
            elif regex_of_ticker.match(request.lower()):
                answer = get_ticker_info_from_binance(request)
            else:
                answer = "Чтооо??? Я тебя не понимаю, попробуй ввести другую команду!"
        else:
            answer = "Выбери сначала биржу, с которой хочешь получать информацию!"

        bot.send_message(message.chat.id, answer)

    bot.polling()


if __name__ == '__main__':
    print('KAKZHEYAZAEBALSYA')
    telegram_bot(token)
