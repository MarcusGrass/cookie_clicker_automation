import logging
import unittest

from .loggers import get_loggers


class LoggingTester(unittest.TestCase):

    def test_multiple_loggers(self):
        names = ["info", "warning", "critical"]
        levels = [logging.INFO, logging.WARNING, logging.CRITICAL]
        get_loggers(names, levels)
        info_logger = logging.getLogger("info")
        info_logger.info("Test info msg")
        info_logger.info("Another for info")

        warning_logger = logging.getLogger("warning")
        warning_logger.warning("Warning")

        critical_logger = logging.getLogger("critical")
        critical_logger.critical("shit.")


if __name__ == "__main__":
    unittest.main()
