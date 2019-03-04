import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt
from pandas.plotting import register_matplotlib_converters


def ema(samples, current_day, day_count):
    a, b = 0, 0
    one_minus_alpha = 1 - (2 / (day_count - 1))
    for i in range(0, day_count + 1):
        power = pow(one_minus_alpha, i)
        b += power
        if current_day - i > 0:
            a += power * samples[current_day - i]
        else:
            a += power * samples[0]
            return a / b
    return a / b


def buy(prices, index, budget, stock):
    if budget >= prices[index]:
        quantity = budget // prices[index]
        full_price = quantity * prices[index]
        return budget - full_price, stock + quantity
    else:
        return budget, stock


def sell(prices, index, budget, stock):
    if stock > 0:
        value = stock * prices[index]
        return budget + value, 0
    else:
        return budget, stock


if __name__ == '__main__':
    register_matplotlib_converters()

    N = 1000
    my_budget = 1000
    my_stock = 0
    macd, signal = [], []

    df = pd.read_csv('netflix.csv')
    prices = df['Close'].tolist()

    for i in range(0, N):
        macd.append(ema(prices, i, 12) - ema(prices, i, 26))
    for i in range(0, N):
        signal.append(ema(macd, i, 9))

    dates = np.array(df['Date'].tolist())
    x = [dt.datetime.strptime(d, '%Y-%m-%d').date() for d in dates]

    x = np.array(x)
    macd = np.array(macd)
    signal = np.array(signal)

    plt.rcParams['figure.figsize'] = [16, 5]

    # Stock prices plot
    f = plt.figure('STOCK')
    plt.title('Netflix Inc.\nStock prices')
    plt.xlabel('Date')
    plt.ylabel('Price [USD]')

    plt.plot(x, prices, label='Price')
    plt.legend(loc='upper right')
    plt.gcf().autofmt_xdate()

    # MACD and SIGNAL plots
    g = plt.figure('MACD')
    plt.title('Netflix Inc.\nMACD & SIGNAL')
    plt.xlabel('Date')
    plt.ylabel('Price [USD]')

    idx = np.argwhere(np.diff(np.sign(macd - signal))).flatten()
    intersection_points = np.array(idx)
    size = len(intersection_points)
    plt.plot(x, macd, label='MACD')
    plt.plot(x, signal, label='SIGNAL')

    print("Before")
    print 'Budget: ', my_budget
    print 'Stock: ', my_stock, '\n'

    for i in range(0, size):
        if macd[intersection_points[i] - 1] > signal[intersection_points[i] - 1]:
            plt.plot(x[intersection_points[i]], signal[intersection_points[i]], 'ro')
            my_budget, my_stock = buy(prices, intersection_points[i], my_budget, my_stock)
        else:
            plt.plot(x[intersection_points[i]], signal[intersection_points[i]], 'bo')
            my_budget, my_stock = sell(prices, intersection_points[i], my_budget, my_stock)

    my_budget, my_stock = sell(prices, intersection_points[i], my_budget, my_stock)
    print("After")
    print 'Budget: ', my_budget
    print 'Stock: ', my_stock
    plt.legend(loc='upper right')
    plt.gcf().autofmt_xdate()

    plt.show()
