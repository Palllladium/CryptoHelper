import requests
from datetime import datetime


def get_ticker_info_from_poloniex(request):
    try:
        names_of_coins = request[5:].split(" to ")
        req = requests.get("https://poloniex.com/public?command=returnTicker")
        info_of_ticker = req.json()[f"{names_of_coins[1].strip().upper()}_{names_of_coins[0].strip().upper()}"]
        items = ["last", "low24hr", "high24hr", "percentChange"]
        answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                 f"Информация по паре {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n\n"
        for item in items:
            map_for_ticker_poloniex = {"last": "Цена последней сделки", "low24hr": "Минимальная цена",
                   "high24hr": "Максимальная цена", "percentChange": "Изменение цены за сутки %"}
            answer += f"{map_for_ticker_poloniex[item]}: {info_of_ticker[item]}\n"
        return answer

    except Exception as ex:
        print(ex)

        return "Оооу... Что-то пошло не так, возможно, данная пара не торгуется на выбранной вами бирже," \
               " попробуйте снова все снова:("


def get_orders_info_from_poloniex(request):
    try:
        names_of_coins = request[6:].split(" to ")
        req = requests.get(f"https://poloniex.com/public?command=returnOrderBook&currencyPair="
                           f"{names_of_coins[1].strip().upper()}_{names_of_coins[0].strip().upper()}&depth=5")
        info_of_orders = req.json()
        items = ["asks", "bids"]
        answer = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" \
                 f"Наиболее выгодные предложения по паре" \
                 f" {names_of_coins[0].strip()} to {names_of_coins[1].strip()}:\n"
        for item in items:
            array_of_orders = info_of_orders[item]
            map_for_orders_yobit = {"asks": "Покупка", "bids": "Продажа"}
            answer += f"\n{map_for_orders_yobit[item]}:\n"
            for order in array_of_orders:
                answer += f"Цена: {order[0]},   Объем: {order[1]}\n"
        return answer

    except Exception as ex:
        print(ex)
        return "Оооу... Что-то пошло не так, возможно, данная пара не торгуется на выбранной вами бирже," \
               " попробуйте снова все снова:("
