import unittest
import matplotlib.pyplot as plt
from graphing import Grapher
import datetime
import time


class GraphTests(unittest.TestCase):

    def test_plotting(self):
        example_heavenly_chips = [100, 1100, 5000, 7700, 10000]
        example_timestamps = [0, 300, 600, 900, 1200]
        plt.plot(example_timestamps, example_heavenly_chips)
        plt.show()

    def test_grapher(self):
        grapher = Grapher(2000)
        time.sleep(3)
        grapher.update_and_draw(2010)
        time.sleep(3)
        grapher.update_and_draw(2020)
        time.sleep(7)
        grapher.update_and_draw(2030)


if __name__ == "__main__":
    pass
