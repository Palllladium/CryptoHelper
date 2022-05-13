import requests
from datetime import datetime
import telebot
from auth_data import token
import re
from telebot import types


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Hello friend! Write the 'price' to find out the cost of BTC!")

    regex_of_ticker = re.compile("price[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z]{2,6}[\s]*")
    regex_of_depth = re.compile("orders[\s]+[a-z]{2,6}[\s]+to[\s]+[a-z\s]{2,6}[\s]*")

    @bot.message_handler(content_types=["text"])
    def send_text(message):

        # current orders
        if regex_of_depth.match(message.text.lower()):
            try:
                names_of_coins = message.text.lower()[7:].split(" to ")
                req = requests.get(f"https://yobit.net/api/3/depth/"
                                   f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}"
                                   f"?limit={5}&ignore_invalid=1")
                response = req.json()
                info_of_orders = response[f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}"]
                items = ["Asks", "Bids"]
                answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                         f"Actual the most profitable orders of" \
                         f" {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n"

                for item in items:
                    array_of_orders = info_of_orders[item.lower()]
                    answer += f"\n{item}:\n"
                    for order in array_of_orders:
                        answer += f"Price: {order[0]},   Volume: {order[1]}\n"

                bot.send_message(
                    message.chat.id,
                    answer
                )

            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "Damn...Something was wrong..."
                )

        elif regex_of_ticker.match(message.text.lower()):
            try:
                names_of_coins = message.text.lower()[6:].split(" to ")
                req = requests.get(f"https://yobit.net/api/3/ticker/"
                                   f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}")
                response = req.json()
                info_of_ticker = response[f"{names_of_coins[0].strip()}_{names_of_coins[1].strip()}"]
                items = ["High", "Low", "Avg", "Vol", "Last", "Buy", "Sell"]
                answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                         f"Sell {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n\n"
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
                    "Damn...Something was wrong..."
                )

        else:
            bot.send_message(message.chat.id, "Whaaat??? Check the command dude!")

    bot.polling()


if __name__ == '__main__':
    # get_data()
    print('KAKZHEYAZAEBALSYA')
    telegram_bot(token)
