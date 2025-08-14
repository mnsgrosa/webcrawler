import logging
import sys

class MyLogger:
    def __init__(self, logger_name = __name__):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(stream_handler)