import matplotlib.pyplot as plt
from datetime import datetime
from logger_classes.loggers import LoggingCollector


class Grapher(object):
    def __init__(self, heavenly_chips, lc):
        self.heavenly_chips = [heavenly_chips]
        self.derivative_chips = [heavenly_chips]
        self.timestamps = [0]
        self.derivative = [0]
        self.derivative_timestamps = [0]
        self.starttime = datetime.now()
        self.last_derivative_time = datetime.now()
        self.lc = lc
        self.lc.warn("Initialized grapher.")

    def update_and_draw(self, heavenly_chip_count):
        self.heavenly_chips.append(heavenly_chip_count)
        current_time_in_seconds = (datetime.now() - self.starttime).seconds
        self.timestamps.append(current_time_in_seconds)
        self.draw_regular_plot()
        if self.time_to_take_derivative():
            self.derivative_chips.append(heavenly_chip_count)
            self.derivative_timestamps.append(current_time_in_seconds)
            self.calculate_simple_derivative()
            self.draw_derivative_plot()
            self.last_derivative_time = datetime.now()

    def draw_regular_plot(self):
        plt.plot(self.timestamps, self.heavenly_chips, 'b')
        plt.savefig('D:\\Program\\PycharmProjects\\seleniumtest\\logs\\heavenly_plot.png')
        plt.close()

    def draw_derivative_plot(self):
        plt.plot(self.derivative_timestamps, self.derivative, 'r')
        plt.savefig('D:\\Program\\PycharmProjects\\seleniumtest\\logs\\heavenly_derivative.png')
        plt.close()
        self.lc.warn("Drew derivative.")

    def calculate_simple_derivative(self):
        derivative = (self.derivative_chips[-1] - self.derivative_chips[-2]) / \
                     (self.derivative_timestamps[-1] - self.derivative_timestamps[-2])
        self.derivative.append(derivative)

    def time_to_take_derivative(self):
        if (datetime.now() - self.last_derivative_time).seconds > 600:
            return True
        return False


