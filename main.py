import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.lines as ln
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
    BUDGET = 1000
    N = 1000
    my_budget = BUDGET
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

    plt.rcParams['figure.figsize'] = [16, 9]

    # Stock prices plot
    plt.figure('Netflix Inc.')
    stock_plot = plt.subplot(2, 1, 1)
    plt.axis([x[0], x[N - 1], 0, 450])
    # plt.axis([x[N - 1 - 400], x[N - 1], 150, 450])    # 300 ostatnich dni
    plt.title('Stock prices')
    plt.xlabel('Date')
    plt.ylabel('Price [USD]')
    plt.grid(which='major', axis='both', alpha=0.3)
    plt.plot(x, prices, label='Price')
    plt.legend(loc='upper left')

    # MACD and SIGNAL plots
    plt.subplot(2, 1, 2)
    plt.axis([x[0], x[N - 1], -40, 40])
    # plt.axis([x[N - 1 - 400], x[N - 1], -30, 40])     # 300 ostatnich dni
    plt.title('MACD & SIGNAL')
    plt.xlabel('Date')
    plt.ylabel('Price [USD]')
    plt.grid(which='major', axis='both', alpha=0.3)

    idx = np.argwhere(np.diff(np.sign(macd - signal))).flatten()
    intersection_points = np.array(idx)
    size = len(intersection_points)
    plt.plot(x, macd, label='MACD')
    plt.plot(x, signal, label='SIGNAL')
    plt.legend(loc='upper left')

    # Intersection plot
    for i in range(0, size):
        if macd[intersection_points[i]] > signal[intersection_points[i]]:
            plt.plot(x[intersection_points[i]], signal[intersection_points[i]], 'bo')
            if macd[intersection_points[i]] > 0:
                my_budget, my_stock = sell(prices, intersection_points[i], my_budget, my_stock)
                plt.axvline(x[intersection_points[i]], ymin=0.5, ymax=1, color="green", alpha=0.4)
        else:
            plt.plot(x[intersection_points[i]], signal[intersection_points[i]], 'ro')
            if macd[intersection_points[i]] < 0:
                my_budget, my_stock = buy(prices, intersection_points[i], my_budget, my_stock)
                plt.axvline(x[intersection_points[i]], ymin=0, ymax=0.5, color="red", alpha=0.4)

    stock_worth = my_stock * prices[N - 1]
    profit = (my_budget + stock_worth) - BUDGET
    print('Starting budget: {}$'.format(BUDGET))
    print('Budget now: {0:.2f}$'.format(my_budget))
    print('Stock now: ', my_stock)
    print('Stock worth: {0:.2f}$'.format(round(stock_worth, 2)))
    print('Earned: {0:.2f}$'.format(round(profit, 2)))
    print('Profit: {0:.2f}%'.format(round((profit / BUDGET) * 100, 2)))

    plt.tight_layout()
    plt.show()
