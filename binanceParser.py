import requests
from datetime import datetime


def get_ticker_info_from_binance(request):
    try:
        names_of_coins = request[5:].split(" to ")
        req = requests.get(f"https://api.binance.com/api/v1/ticker/24hr?symbol="
                           f"{names_of_coins[0].strip().upper()}{names_of_coins[1].strip().upper()}")
        info_of_ticker = req.json()
        items = ["lastPrice", "lowPrice", "highPrice", "bidPrice", "askPrice",
                 "weightedAvgPrice", "priceChangePercent", "volume"]
        answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                 f"Информация по паре {names_of_coins[0].strip()} " \
                 f"to {names_of_coins[1].strip()}:\n\n"
        for item in items:
            map_for_ticker_binance = {"lastPrice": "Цена последней сделки", "lowPrice": "Минимальная цена",
                                      "highPrice": "Максимальная цена", "bidPrice": "Цена покупки",
                                      "askPrice": "Цена продажи",
                                      "weightedAvgPrice": "Средневзвешенная цена",
                                      "priceChangePercent": "Изменение цены за сутки %",
                                      "volume": "Объем торгов базовой валюты"}
            answer += f"{map_for_ticker_binance[item]}: {info_of_ticker[item]}\n"
        return answer

    except Exception as ex:
        print(ex)

        return "Оооу... Что-то пошло не так, возможно, данная " \
               "пара не торгуется на выбранной вами бирже," \
               " попробуйте снова все снова:("


def get_orders_info_from_binance(request):
    try:
        names_of_coins = request[6:].split(" to ")
        req = requests.get(f"https://api.binance.com/api/v1/depth?symbol="
                           f"{names_of_coins[0].strip().upper()}{names_of_coins[1].strip().upper()}&limit=5")
        info_of_orders = req.json()
        items = ["asks", "bids"]
        answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                 f"Наиболее выгодные предложения по паре" \
                 f" {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n"
        for item in items:
            array_of_orders = info_of_orders[item]
            map_for_orders_binance = {"asks": "Покупка", "bids": "Продажа"}
            answer += f"\n{map_for_orders_binance[item]}:\n"
            for order in array_of_orders:
                answer += f"Цена: {order[0]},   Объем: {order[1]}\n"
        return answer

    except Exception as ex:
        print(ex)
        return "Оооу... Что-то пошло не так, возможно, данная " \
               "пара не торгуется на выбранной вами бирже," \
               " попробуйте снова все снова:("
