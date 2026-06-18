# Импортируем модуль json для чтения и записи данных в формате JSON
import json

# Импортируем Path для построения путей к файлам и папкам
from pathlib import Path

# Импортируем наш модуль логирования для записи событий
from src.logger import setup_logger

# Импортируем модель Note для работы с данными заметок
from src.models import Note

# Создаём логгер для этого модуля — все действия будут записываться в журнал
logger = setup_logger("fs_driver")


# Создаём класс FSDriver — это драйвер для работы с файловой системой
# Все операции чтения/записи файлов происходят только через этот класс
class FSDriver:
    """
    Драйвер файловой системы для приложения Notes.

    Отвечает за:
    - Создание папки для хранения данных (если её нет)
    - Сохранение заметок в JSON-файлы
    - Загрузку заметок из JSON-файлов
    - Удаление заметок
    - Проверку существования файлов
    """

    # Конструктор класса — вызывается при создании нового объекта FSDriver
    def __init__(self, data_dir: Path) -> None:
        """
        Инициализирует драйвер файловой системы.

        Аргументы:
            data_dir: путь к папке, где хранятся данные заметок
        """
        # Сохраняем путь к папке данных как атрибут объекта
        self.data_dir = data_dir

        # Создаём папку для данных, если она ещё не существует
        # parents=True — создаёт все промежуточные папки
        # exist_ok=True — не падает, если папка уже есть
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Логируем, что папка данных готова к работе
        logger.info(f"Папка данных готова: {self.data_dir}")

    # Метод: получить полный путь к JSON-файлу заметки по её заголовку
    def _get_note_path(self, note_id: str) -> Path:
        """
        Возвращает путь к JSON-файлу заметки.

        Файлы сохраняются с именем based on ID заметки,
        чтобы избежать проблем с спецсимволами в заголовках.

        Аргументы:
            note_id: уникальный идентификатор заметки

        Возвращает:
            Объект Path — полный путь к файлу
        """
        return self.data_dir / f"{note_id}.json"

    # Метод: сохранить одну заметку в JSON-файл
    def save_note(self, note: Note) -> bool:
        """
        Сохраняет заметку в JSON-файл.

        Если файл уже существует — перезаписывает его.
        При ошибке логирует проблему и возвращает False.

        Аргументы:
            note: объект Note для сохранения

        Возвращает:
            True если сохранение прошло успешно, False при ошибке
        """
        try:
            # Получаем путь к файлу заметки
            file_path = self._get_note_path(note.id)

            # Превращаем заметку в словарь (модель → dict → JSON)
            note_data = note.to_dict()

            # Открываем файл для записи (кодировка UTF-8 для русского текста)
            with open(file_path, "w", encoding="utf-8") as f:
                # Записываем словарь в файл с отступами для читаемости
                json.dump(note_data, f, ensure_ascii=False, indent=2)

            # Логируем успешное сохранение
            logger.info(f"Заметка сохранена: '{note.title}' (ID: {note.id})")
            return True

        except (IOError, OSError) as e:
            # Если произошла ошибка файловой операции — логируем и возвращаем False
            logger.error(f"Ошибка сохранения заметки '{note.title}': {e}")
            return False

    # Метод: загрузить одну заметку из JSON-файла
    def load_note(self, note_id: str) -> Optional[Note]:
        """
        Загружает заметку из JSON-файла по её идентификатору.

        Аргументы:
            note_id: уникальный идентификатор заметки

        Возвращает:
            Объект Note если файл найден, None если файла нет
        """
        try:
            # Получаем путь к файлу заметки
            file_path = self._get_note_path(note_id)

            # Проверяем, существует ли файл
            if not file_path.exists():
                logger.warning(f"Файл заметки не найден: {file_path}")
                return None

            # Открываем файл и читаем данные
            with open(file_path, "r", encoding="utf-8") as f:
                note_data = json.load(f)

            # Создаём объект Note из прочитанного словаря
            note = Note.from_dict(note_data)

            # Логируем успешную загрузку
            logger.info(f"Заметка загружена: '{note.title}' (ID: {note.id})")
            return note

        except (json.JSONDecodeError, IOError) as e:
            # Если файл повреждён или не читается — логируем ошибку
            logger.error(f"Ошибка загрузки заметки {note_id}: {e}")
            return None

    # Метод: загрузить ВСЕ заметки из папки данных
    def load_all_notes(self) -> list:
        """
        Загружает все заметки из папки данных.

        Перебирает все JSON-файлы в папке data и создаёт из них объекты Note.

        Возвращает:
            Список объектов Note (может быть пустым, если заметок нет)
        """
        # Создаём пустой список для хранения загруженных заметок
        notes = []

        # Перебираем все файлы в папке данных
        for file_path in self.data_dir.glob("*.json"):
            try:
                # Открываем каждый JSON-файл и читаем данные
                with open(file_path, "r", encoding="utf-8") as f:
                    note_data = json.load(f)

                # Создаём объект Note из словаря
                note = Note.from_dict(note_data)

                # Добавляем заметку в список
                notes.append(note)

            except (json.JSONDecodeError, IOError) as e:
                # Если конкретный файл повреждён — пропускаем его, но логируем
                logger.warning(f"Пропуск повреждённого файла {file_path.name}: {e}")
                continue

        # Логируем количество загруженных заметок
        logger.info(f"Загружено заметок: {len(notes)}")
        return notes

    # Метод: удалить заметку по её идентификатору
    def delete_note(self, note_id: str) -> bool:
        """
        Удаляет JSON-файл заметки.

        Аргументы:
            note_id: уникальный идентификатор заметки для удаления

        Возвращает:
            True если удаление прошло успешно, False при ошибке
        """
        try:
            # Получаем путь к файлу заметки
            file_path = self._get_note_path(note_id)

            # Проверяем, существует ли файл перед удалением
            if not file_path.exists():
                logger.warning(f"Попытка удаления несуществующей заметки: {note_id}")
                return False

            # Удаляем файл
            file_path.unlink()

            # Логируем успешное удаление
            logger.info(f"Заметка удалена: ID {note_id}")
            return True

        except OSError as e:
            # Если не удалось удалить файл — логируем ошибку
            logger.error(f"Ошибка удаления заметки {note_id}: {e}")
            return False

    # Метод: проверить, существует ли заметка с таким идентификатором
    def note_exists(self, note_id: str) -> bool:
        """
        Проверяет, есть ли файл заметки на диске.

        Аргументы:
            note_id: уникальный идентификатор заметки

        Возвращает:
            True если файл существует, False если нет
        """
        return self._get_note_path(note_id).exists()
