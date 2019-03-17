import matplotlib.pyplot as plt
from datetime import datetime
import math


class Grapher(object):
    def __init__(self, heavenly_chips, balance, compensator, lc):
        self.heavenly_chips = [heavenly_chips]
        self.log_heavenly_chips = [math.log2(heavenly_chips)]

        self.derivative_chips = [heavenly_chips]

        self.amount = [balance.amount]
        self.log_amount = [math.log2(balance.amount)]

        self.cps = list()
        self.log_cps = list()
        self.cps_timestamps = list()
        self.cps_initialized = False

        self.timestamps = [0]

        self.derivative = [0]
        self.log_derivative = [0]
        self.derivative_timestamps = [0]

        self.starttime = datetime.now()
        self.last_derivative_time = datetime.now()
        self.lc = lc
        self.lc.warn("Initialized grapher.")

        if clear_to_draw_cps(compensator):
            self.init_cps_plot(balance.cps)

    def update_and_draw(self, heavenly_chip_count, balance, compensator):
        self.heavenly_chips.append(heavenly_chip_count)
        self.log_heavenly_chips.append(math.log2(heavenly_chip_count))

        self.amount.append(balance.amount)
        self.log_amount.append(math.log2(balance.amount))

        current_time_in_seconds = (datetime.now() - self.starttime).seconds
        self.timestamps.append(current_time_in_seconds)
        self.draw_regular_plot()
        self.draw_amount_plot()
        if self.time_to_take_derivative():
            self.derivative_chips.append(heavenly_chip_count)
            self.derivative_timestamps.append(current_time_in_seconds)
            self.calculate_simple_derivative()
            self.draw_derivative_plot()
            self.last_derivative_time = datetime.now()

        if clear_to_draw_cps(compensator) and self.cps_initialized and balance.cps/self.cps[-1] < 10:
            self.cps.append(balance.cps)
            self.log_cps.append(math.log2(balance.cps))

            self.cps_timestamps.append(current_time_in_seconds)
            self.draw_cps_plot()
        elif clear_to_draw_cps(compensator) and self.cps_initialized is False:
            self.init_cps_plot(balance.cps)

    def draw_regular_plot(self):
        draw_plot(self.timestamps, self.heavenly_chips, self.log_heavenly_chips, "chips")

    def draw_amount_plot(self):
        draw_plot(self.timestamps, self.amount, self.log_amount, "amount")

    def draw_cps_plot(self):
        draw_plot(self.cps_timestamps, self.cps, self.log_cps, "cps")

    def draw_derivative_plot(self):
        draw_plot(self.derivative_timestamps, self.derivative, self.log_derivative, "derivative")

    def calculate_simple_derivative(self):
        derivative = (self.derivative_chips[-1] - self.derivative_chips[-2]) / \
                     (self.derivative_timestamps[-1] - self.derivative_timestamps[-2])
        self.derivative.append(derivative)
        log_derivative = math.log2(derivative)
        self.log_derivative.append(log_derivative)

    def time_to_take_derivative(self):
        if (datetime.now() - self.last_derivative_time).seconds > 600:
            return True
        return False

    def init_cps_plot(self, cps):
        self.cps_timestamps = [0]
        self.cps.append(cps)
        self.log_cps.append(math.log2(cps))
        self.cps_initialized = True


def clear_to_draw_cps(cps_compensator):
    if cps_compensator != 50:
        return True
    return False


def draw_plot(x, y1, y2, name):
    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('absolute', color=color)
    ax1.plot(x, y1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel('log', color=color)  # we already handled the x-label with ax1

    y_ticks = get_yticks(y2)
    ax2.plot(x, y2, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_yticks(y_ticks)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    fig.savefig('D:\\Program\\PycharmProjects\\seleniumtest\\logs\\' + name + '.png')
    plt.close()


def get_yticks(y2):
    end_of_range = int(math.ceil(max(y2)))+1
    start_of_range = int(math.floor(min(y2)))-1
    y_ticks = [n for n in range(start_of_range, end_of_range)]
    return y_ticks
