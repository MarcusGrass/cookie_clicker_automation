import logging


class LoggingCollector(object):
    def __init__(self):
        get_loggers(["info", "warning", "critical", "debug"], [logging.INFO, logging.WARNING,
                                                               logging.CRITICAL, logging.DEBUG])
        self.info_logger = logging.getLogger("info")
        self.warn_logger = logging.getLogger("warning")
        self.critical_logger = logging.getLogger("critical")
        self.debug_logger = logging.getLogger("debug")

    def info(self, message):
        self.info_logger.info(message)

    def warn(self, message):
        self.warn_logger.warning(message)

    def critical(self, message):
        self.critical_logger.critical(message)

    def debug(self, message):
        self.debug_logger.debug(message)


def get_loggers(names, levels):
    filenames = list()
    for name in names:
        filenames.append('D:\\Program\\PycharmProjects\\seleniumtest\\logs\\' + name + ".log")

    for ind in range(len(names)):
        set_up_loggers(names[ind], filenames[ind], levels[ind])


def set_up_loggers(logger_name, file_name, level):
    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = logging.FileHandler(file_name, mode='a')
    file_handler.setFormatter(formatter)
    log_setup.setLevel(level)
    log_setup.addHandler(file_handler)
