import logging


class Log:

    def __init__(self):
        self.formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
        self.hdlr = logging.StreamHandler()
        self.hdlr.setFormatter(self.formatter)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.hdlr)

    def info(self, content):
        self.logger.info(content)

    def warning(self, content):
        self.logger.warning(content)

    def error(self, content):
        self.logger.error(content)

    def debug(self, content):
        self.logger.debug(content)