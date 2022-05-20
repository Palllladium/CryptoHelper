import telebot
from auth_data import token
import re
from telebot import types
from yobitParser import get_orders_info_from_yobit, get_ticker_info_from_yobit
from poloniexParser import get_orders_info_from_poloniex, get_ticker_info_from_poloniex
from binanceParser import get_orders_info_from_binance, get_ticker_info_from_binance
from infoForSubscribers import get_actual_price, get_changes
import time


def telegram_bot(token):
    bot = telebot.TeleBot(token)
    request = ""
    current_exchange = ""
    is_subscribe = False

    def timer_subscribe():
        nonlocal is_subscribe
        try:
            while is_subscribe:
                messages_for_subscribers = get_changes().split("\n")
                for message in messages_for_subscribers:
                    info_about_message = message.split(":")
                    print(message)
                    if info_about_message[0] != "" and info_about_message[0] != "\n":
                        bot.send_message(int(info_about_message[0].split(" ")[0]), info_about_message[1].strip())
                        bot.send_message(int(info_about_message[0].split(" ")[0]),
                                         "Если хотите снова получить уведомление об изменении цены на данную пару или"
                                         " любую другую, оформите подписку снова, используя /subscribe")
                        pattern = re.compile(re.escape(info_about_message[0]))
                        with open('dataSubscribe.txt', 'r+') as f:
                            lines = f.readlines()
                            f.seek(0)
                            for line in lines:
                                result = pattern.search(line)
                                if result is None:
                                    f.write(line)
                                f.truncate()
                        with open('dataSubscribe.txt', 'r') as f:
                            lines = f.readlines()
                            if not lines:
                                is_subscribe = False
                time.sleep(1800)

        except Exception as ex:
            print(ex)

    @bot.message_handler(commands=["subscribe"])
    def subscribe(message):
        bot.send_message(message.chat.id, "Чтобы получать сообщения об изменениях цены на пару, напиши с какой биржи"
                                          " хочешь получать информацию, о какой паре валют и об изменении на сколько "
                                          "процентов тебя стоит уведомлять:\n"
                                          "Пример:\n"
                                          "Subscribe: Binance, btc to usdt, 10")

    @bot.message_handler(commands=["mysubscribes"])
    def subscribe(message):
        answer = "Твои текущие подписки:\n\n"
        with open('dataSubscribe.txt', 'r') as f:
            for line in f:
                data = line.split(" ")
                if data[0] == str(message.chat.id):
                    answer += f"{data[1]}, {data[2]} to {data[4]}, percent: {data[5]}% start price: {data[6]}"
        if answer == "Твои текущие подписки:\n\n":
            answer = "К сожалению, ты не отслеживаешь ни одну из пар..."
        bot.send_message(message.chat.id, answer)

    @bot.message_handler(commands=["unsubscribe"])
    def subscribe(message):
        nonlocal is_subscribe
        pattern = re.compile(re.compile(f"^{message.chat.id}"))
        with open('dataSubscribe.txt', 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            for line in lines:
                result = pattern.search(line)
                if result is None:
                    f.write(line)
                f.truncate()
        with open('dataSubscribe.txt', 'r') as f:
            lines = f.readlines()
            if not lines:
                is_subscribe = False
        bot.send_message(message.chat.id, "Ты отписался от всех оповещений!")

    @bot.message_handler(commands=["help"])
    def help_message(message):
        bot.send_message(message.chat.id,
                         "Нажмите кнопку \"Price\" или введите команду /price чтобы получить статистическую информацию"
                         " о торгах за последние 24 часа по паре монет, которая вас интересует.\n"
                         "Нажмите \"Orders\" или введите команду /orders чтобы получить информацию о наиболее выгодных"
                         " актуальных предложениях на покупку/продажу интересущей вас пары монет.")

    @bot.message_handler(commands=["price", "orders"])
    def command_message(message):
        nonlocal request
        request = ""
        request += f"{message.text[1:]} "
        bot.send_message(message.chat.id, 'Введите пару монет, по которой хотите получить информацию.\n'
                                          'Пример: btc to usdt')

    @bot.message_handler(commands=["exchange"])
    def choose_exchange(message):
        markup_inline = types.InlineKeyboardMarkup()
        item_poloniex = types.InlineKeyboardButton(text='Poloniex', callback_data='Poloniex')
        item_yobit = types.InlineKeyboardButton(text='Yobit', callback_data='Yobit')
        item_binance = types.InlineKeyboardButton(text='Binance', callback_data='Binance')
        markup_inline.add(item_poloniex, item_yobit, item_binance)
        bot.send_message(message.chat.id, "Выбери биржу, с которой хочешь получать инфомацию.\n"
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
        bot.send_message(message.chat.id, "Выбери биржу, с которой хочешь получать инфомацию.\n"
                                          "Позже ты сможешь изменить это позже с помощью команды /exchange",
                         reply_markup=markup_inline)

    @bot.callback_query_handler(func=lambda call: True)
    def answer_of_call(call):
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_price = types.KeyboardButton('/price')
        item_orders = types.KeyboardButton('/orders')
        markup_reply.add(item_price, item_orders)
        bot.send_message(call.message.chat.id, f"Отлично, ты выбрал биржу {call.data}\n"
                                               f"Теперь выбери, что ты хочешь узнать: "
                                               f"информацию о паре или актуальные"
                                               f" предложения покупки/продажи.",
                         reply_markup=markup_reply
                         )
        nonlocal current_exchange
        current_exchange = call.data

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        regex_of_subscribe = re.compile("Subscribe: [a-zA-Z]+")
        if regex_of_subscribe.match(message.text):
            data = f"{message.chat.id} {' '.join(message.text[11:].split(', '))} "
            if len(message.text[11:].split(', ')) == 3:
                old_coin_price = get_actual_price(data)
                data += f"{old_coin_price}"
            data += f"\n"
            already_contain = False
            with open("dataSubscribe.txt", "r") as f:
                for line in f:
                    if line == data:
                        already_contain = True
            if not already_contain:
                with open("dataSubscribe.txt", "a") as f:
                    f.write(data)
            bot.send_message(message.chat.id, "Отлично, подписка выполнена!")
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
    telegram_bot(token)
