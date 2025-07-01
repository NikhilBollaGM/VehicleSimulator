import logging
from datetime import datetime

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            logging.basicConfig(
                filename='app.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        return cls._instance

    @classmethod
    def log(cls, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f'[{timestamp}] [INFO] {message}'
        print(formatted_message)  # Optional: keep console output
        logging.info(message)
