import requests


def get_actual_price(data):
    info_of_ticker = 0
    try:
        info_of_user = data.split(" ")
        if info_of_user[1] == "Binance":
            req = requests.get(f"https://api.binance.com/api/v1/ticker/24hr?symbol="
                               f"{info_of_user[2].strip().upper()}{info_of_user[4].strip().upper()}")
            info_of_ticker = req.json()["lastPrice"]
        elif info_of_user[1] == "Yobit":
            req = requests.get(f"https://yobit.net/api/3/ticker/"
                               f"{info_of_user[2].strip()}_{info_of_user[4].strip()}")
            info_of_ticker = req.json()[f"{info_of_user[2].strip()}_{info_of_user[4].strip()}"]["last"]
        elif info_of_user[1] == "Poloniex":
            req = requests.get("https://poloniex.com/public?command=returnTicker")
            info_of_ticker = req.json()[f"{info_of_user[4].strip().upper()}_{info_of_user[2].strip().upper()}"]["last"]

        return info_of_ticker

    except Exception as ex:
        print(ex)
        return "Оооу... Что-то пошло не так, возможно, данная пара " \
               "перестала торговаться на выбранной вами бирже," \
               " попробуйте ввести /subscribe ещё раз."


def get_changes():
    answer = ""
    with open("dataSubscribe.txt", "r") as f:
        for line in f:
            clear_line = line.rstrip("\n")
            data = clear_line.split(" ")
            old_price = data[6]
            actual_price = get_actual_price(clear_line)
            price_change = (float(actual_price) - float(old_price)) / float(old_price) * 100
            if float(price_change) >= float(clear_line.split()[5]):
                answer += f"{clear_line}: Проверьте биржу {data[1]}! " \
                          f"Цена для пары {data[2].upper()}/{data[4].upper()} " \
                          f"изменилась на {str(round(price_change, 3))}%!\n"
    return answer

