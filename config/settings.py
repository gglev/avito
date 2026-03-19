import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# Loading the variables
load_dotenv()

class Settings: # This class is used to store all settings of project
    def __init__(self):
        self._setup_directories()
        self._load_settings()
        self._setup_logging()
    
    def _setup_directories(self):
        self.BASE_DIR = Path(__file__).parent.parent # create a main folders for project

        self.DATA_DIR = self.BASE_DIR 
        self.MODELS_DIR = self.BASE_DIR 
        self.LOGS_DIR = self.BASE_DIR 
        self.TRAINING_DIR = self.BASE_DIR 
        self.IMAGES_DIR = self.BASE_DIR 

        for directory in [self.DATA_DIR, self.MODELS_DIR,
                self.LOGS_DIR, self.TRAINING_DIR, self.IMAGES_DIR ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_settings(self):
        self.TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        if not self.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN is not find in .env file.")
        
        self.CHAT_ID = os.getenv('CHAT_ID')
        if not self.CHAT_ID:
            raise ValueError("CHAT_ID is not find in .env file.")
        
        # url avito
        self.BASE_URL = "https://www.avito.ru/"
        self.SEARCH_URL = "https://www.avito.ru/all/knigi_i_zhurnaly/knigi-ASgBAgICAUTOAuoK?context=H4sIAAAAAAAA_wE9AML_YToyOntzOjg6ImZyb21QYWdlIjtzOjU6InNzZmF2IjtzOjk6ImZyb21fcGFnZSI7czo1OiJzc2ZhdiI7fQMFMC09AAAA&localPriority=0&s=104"

        #proxy
        self.PROXY_URL = os.getenv('PROXY_URL')
        self.PROXY_ENABLED = bool(self.PROXY_URL)

        self.CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL','120'))

        # are working
        self.DEBUG = os.getenv('DEBUG', 'false').lower == 'true'

        self.DEVICE = self._detect_device()
        self.USE_GPU = self.DEVICE == "cuda"
        self.USE_8BIT = True # use bitsandbyres for data economy

        self.TEXT_MODEL_PATH = self.MODELS_DIR / "text_model"
        self.IMAGE_MODEL_PATH = self.MODELS_DIR / "image_model"
        self.PRICE_MODEL_PATH = self.MODELS_DIR / "price_model.pkl"

        # settings for learning
        self.MIN_FOR_TRAINING = 5
        self.TRAINING_EPOCHS = 300
        self.LEARNING_RATE = 0.001

        #limits
        self.MAX_ITEMS_PER_PAGE = 20
        self.REQUEST_TIMEOUT = 30
        self.MAX_IMAGES_PER_BOOK = 5

        # roots to files
        self.SEEN_IDS_FILE = self.DATA_DIR / "seen_ids.txt"
        self.TRAINING_DATA_FILE = self.TRAINING_DIR / "data" / "training_data.json"
        self.LOG_FILE = self.LOGS_DIR / "bot.log"

    def _detect_device(self) -> str:
        # define available devices
        # returns: str: 'cuda', 'mps' or 'cpu'

        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch,"backends") and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps" # for ios
            else:
                return "cpu"
        except ImportError:
            return "cpu"
    def _setup_logging(self):
        log_level = logging.DEBUG if self.DEBUG else logging.INFO

        logging.basicConfig(
            level = log_level,
            format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers = [
                logging.FileHandler(self.LOG_FILE, encoding = 'utf-8'),
                logging.StreamHandler()
            ]
        )

        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)

        self.logger = logging.getLogger(__name__)
        self.logger.info("Log system is completed")

        def get_proxy_dict(self) -> Optional[Dict[str,str]]:
            if self.PROXY_ENABLED and self.PROXY_URL:
                return {
                    'http' : self.PROXY_URL,
                    'https' : self.PROXY_URL
                }
            return None
        
        def get_device_info(self) -> str:
            if self.USE_GPU:
                import torch
                if self.DEVICE == "cuda":
                    gpu_name = torch.cuda.get_device_name(0)
                    return f"GPU {gpu_name}"
                elif self.DEVICE == "mps":
                    return "MPS"
            return "CPU"
        
        def __repr__(self) -> str:
             return f"""
📁 Конфигурация проекта:
    Telegram Token: {'✅' if self.TELEGRAM_TOKEN else '❌'}
    Chat ID: {self.CHAT_ID}
    Прокси: {'✅' if self.PROXY_ENABLED else '❌'}
    Интервал проверки: {self.CHECK_INTERVAL} сек
    {self.get_device_info()}
    Режим отладки: {self.DEBUG}
    
📂 Директории:
    Данные: {self.DATA_DIR}
    Модели: {self.MODELS_DIR}
    Логи: {self.LOGS_DIR}
    Обучение: {self.TRAINING_DIR}
"""

settings = Settings()

__all__ = ['settings']
