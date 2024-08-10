import os
import logging
from logging.handlers import TimedRotatingFileHandler


class ExchangeLogger:
    def __init__(self, exchange_code):
        self.exchange_code = exchange_code
        self.logger = logging.getLogger(f"{self.exchange_code}")
        self.logger.setLevel(logging.DEBUG)

        log_directory = f"logs/"
        file_name = f"{self.exchange_code}.log"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        
        self.file_handler = TimedRotatingFileHandler(
            f"{log_directory}{file_name}", 
            when='midnight', 
            interval=1, 
            backupCount=7
        )

        # 再创建一个handler，用于输出到控制台
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.INFO)  # 控制台只输出INFO及以上的日志

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)
        self.stream_handler.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(self.file_handler)
        self.logger.addHandler(self.stream_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)