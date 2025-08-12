import logging

class MyLogger:
    def __init__(self, logger_name = __name__):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)