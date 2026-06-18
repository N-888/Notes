# Импортируем модуль logging для ведения журналов событий приложения
import logging

# Импортируем Path для построения путей к файлам и папкам
from pathlib import Path


# Константа: путь к папке проекта (корневая директория)
# Берём директорию, в которой лежит этот файл, и поднимаемся на уровень вверх
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Константа: путь к папке с логами
LOG_DIR = PROJECT_ROOT / "logs"

# Константа: путь к файлу логов
LOG_FILE = LOG_DIR / "notes.log"


def setup_logger(name: str = "notes_app") -> logging.Logger:
    """
    Создаёт и настраивает логгер приложения.

    Логгер пишет сообщения:
    - в файл logs/notes.log (уровень DEBUG и выше)
    - в консоль (уровень INFO и выше)

    Аргументы:
        name: имя логгера (по умолчанию 'notes_app')

    Возвращает:
        Настроенный объект logging.Logger
    """

    # Создаём папку для логов, если она ещё не существует
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Создаём логгер с указанным именем
    logger = logging.getLogger(name)

    # Устанавливаем минимальный уровень логирования — DEBUG (ловим всё)
    logger.setLevel(logging.DEBUG)

    # Проверяем, нет ли уже обработчиков у логгера (чтобы не дублировать)
    if not logger.handlers:

        # --- Обработчик для файла ---
        # Пишет все сообщения от DEBUG и выше в файл
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # --- Обработчик для консоли ---
        # Показывает только INFO и выше (чтобы не засорять консоль)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Формат сообщений: дата-время | уровень | имя модуля | сообщение
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Применяем формат к обоим обработчикам
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Подключаем обработчики к логгеру
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    # Возвращаем готовый логгер
    return logger
