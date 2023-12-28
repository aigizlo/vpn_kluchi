import logging

# Настраиваем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Установите уровень логирования на наивысший уровень, который вам нужен

# Добавляем файловый хендлер логов
file_handler = logging.FileHandler('bot.log')
file_handler.setLevel(logging.DEBUG)  # Уровень для записи в файл (в данном случае, установлен на DEBUG)
logger.addHandler(file_handler)

# Добавляем консольный хендлер логов
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Уровень для вывода на консоль (в данном случае, установлен на DEBUG)
logger.addHandler(console_handler)

# Опционально, настройка формата логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
