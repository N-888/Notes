# Импортируем наш модуль для работы с файловой системой
from src.fs_driver import FSDriver

# Импортируем модель заметки
from src.models import Note

# Импортируем модуль логирования
from src.logger import setup_logger

# Создаём логгер для этого модуля — записываем все действия бизнес-логики
logger = setup_logger("business_logic")


# Создаём класс BusinessLogic — вся бизнес-логика приложения находится здесь
# Этот класс проверяет правила, валидирует данные и управляет заметками
class BusinessLogic:
    """
    Класс бизнес-логики приложения Notes.

    Отвечает за:
    - Валидацию данных (проверка правил перед сохранением)
    - Создание новых заметок
    - Редактирование существующих заметок
    - Удаление заметок
    - Поиск заметок
    - Получение списка всех заметок
    """

    # Конструктор — принимает драйвер файловой системы для работы с данными
    def __init__(self, fs_driver: FSDriver) -> None:
        """
        Инициализирует бизнес-логику.

        Аргументы:
            fs_driver: объект FSDriver для чтения/записи данных
        """
        # Сохраняем ссылку на файловый драйвер
        self.fs = fs_driver

        # Логируем создание объекта бизнес-логики
        logger.info("Бизнес-логика инициализирована")

    # === ВАЛИДАЦИЯ (ПРОВЕРКА ПРАВИЛ) ===

    # Метод: проверить заголовок заметки
    def _validate_title(self, title: str) -> None:
        """
        Проверяет, что заголовок заметки не пустой.

        Бизнес-правило: заголовок обязателен и не может быть пустой строкой.

        Аргументы:
            title: заголовок заметки для проверки

        Вызывает:
            ValueError: если заголовок пустой или содержит только пробелы
        """
        # Убираем пробелы по краям и проверяем длину
        if not title or not title.strip():
            logger.error("Ошибка валидации: заголовок заметки пустой")
            raise ValueError("Заголовок заметки не может быть пустым!")

        # Логируем, что заголовок прошёл проверку
        logger.debug(f"Заголовок прошёл валидацию: '{title}'")

    # Метод: проверить список вложений
    def _validate_attachments(self, attachments: list) -> None:
        """
        Проверяет, что attachments — это список строк.

        Бизнес-правило: attachments должен быть списком, каждый элемент — строка.

        Аргументы:
            attachments: список вложений для проверки

        Вызывает:
            TypeError: если attachments не является списком
            ValueError: если какой-то элемент не является строкой
        """
        # Проверяем, что это именно список
        if not isinstance(attachments, list):
            logger.error("Ошибка валидации: вложения должны быть списком")
            raise TypeError("Вложения должны быть списком!")

        # Проверяем каждый элемент списка
        for item in attachments:
            if not isinstance(item, str):
                logger.error(f"Ошибка валидации: вложение '{item}' не является строкой")
                raise ValueError(f"Каждое вложение должно быть строкой, получено: {type(item)}")

        # Логируем, что вложения прошли проверку
        logger.debug(f"Вложения прошли валидацию: {len(attachments)} шт.")

    # Метод: полная проверка данных заметки перед сохранением
    def _validate_note_data(self, title: str, content: str, attachments: list) -> None:
        """
        Выполняет полную проверку данных заметки перед созданием или редактированием.

        Аргументы:
            title: заголовок заметки
            content: содержимое заметки
            attachments: список вложений

        Вызывает:
            ValueError: если данные не проходят проверку
        """
        # Проверяем заголовок (обязательное поле)
        self._validate_title(title)

        # Проверяем вложения (список строк)
        self._validate_attachments(attachments)

        # Логируем успешную валидацию всех данных
        logger.info(f"Валидация пройдена: заголовок='{title}', контент={len(content)} символов, вложений={len(attachments)}")

    # === ОСНОВНЫЕ ОПЕРАЦИИ ===

    # Метод: создать новую заметку
    def create_note(self, title: str, content: str = "", attachments: list = None) -> Note:
        """
        Создаёт новую заметку и сохраняет её на диск.

        Аргументы:
            title: заголовок заметки (обязательное поле)
            content: текст заметки (по умолчанию пустой)
            attachments: список имён файлов (по умолчанию пустой список)

        Возвращает:
            Созданный объект Note

        Вызывает:
            ValueError: если заголовок пустой или вложения некорректны
        """
        # Если вложения не переданы — используем пустой список
        if attachments is None:
            attachments = []

        # Выполняем валидацию всех данных
        self._validate_note_data(title, content, attachments)

        # Создаём новый объект Note с переданными данными
        new_note = Note(
            title=title.strip(),
            content=content,
            attachments=attachments,
        )

        # Сохраняем заметку на диск через файловый драйвер
        self.fs.save_note(new_note)

        # Логируем успешное создание
        logger.info(f"Создана новая заметка: '{title}' (ID: {new_note.id})")

        # Возвращаем созданную заметку
        return new_note

    # Метод: редактировать существующую заметку
    def update_note(self, note_id: str, title: str = None, content: str = None, attachments: list = None) -> Note:
        """
        Редактирует существующую заметку.

        Можно обновить любое поле или комбинацию полей.
        Поля, которые не переданы (None), остаются без изменений.

        Аргументы:
            note_id: идентификатор заметки для редактирования
            title: новый заголовок (None = не менять)
            content: новый текст (None = не менять)
            attachments: новый список вложений (None = не менять)

        Возвращает:
            Обновлённый объект Note

        Вызывает:
            ValueError: если заголовок пустой или вложения некорректны
            LookupError: если заметка с таким ID не найдена
        """
        # Загружаем существующую заметку с диска
        existing_note = self.fs.load_note(note_id)

        # Если заметка не найдена — выбрасываем ошибку
        if existing_note is None:
            logger.error(f"Попытка редактирования несуществующей заметки: {note_id}")
            raise LookupError(f"Заметка с ID '{note_id}' не найдена!")

        # Обновляем заголовок, если передан новый
        if title is not None:
            # Проверяем, что новый заголовок не пустой
            self._validate_title(title)
            existing_note.title = title.strip()

        # Обновляем содержимое, если передано новое
        if content is not None:
            existing_note.content = content

        # Обновляем вложения, если передан новый список
        if attachments is not None:
            # Проверяем корректность нового списка вложений
            self._validate_attachments(attachments)
            existing_note.attachments = attachments

        # Обновляем время изменения заметки
        existing_note.touch()

        # Сохраняем обновлённую заметку на диск
        self.fs.save_note(existing_note)

        # Логируем успешное редактирование
        logger.info(f"Заметка обновлена: '{existing_note.title}' (ID: {note_id})")

        # Возвращаем обновлённую заметку
        return existing_note

    # Метод: удалить заметку
    def delete_note(self, note_id: str) -> bool:
        """
        Удаляет заметку по её идентификатору.

        Аргументы:
            note_id: идентификатор заметки для удаления

        Возвращает:
            True если удаление прошло успешно, False если заметка не найдена

        Вызывает:
            LookupError: если невозможно удалить при пустом списке (бизнес-правило)
        """
        # Проверяем, существует ли заметка
        if not self.fs.note_exists(note_id):
            logger.warning(f"Попытка удаления несуществующей заметки: {note_id}")
            raise LookupError(f"Заметка с ID '{note_id}' не найдена!")

        # Выполняем удаление через файловый драйвер
        result = self.fs.delete_note(note_id)

        # Логируем результат удаления
        if result:
            logger.info(f"Заметка успешно удалена: ID {note_id}")
        else:
            logger.error(f"Не удалось удалить заметку: ID {note_id}")

        return result

    # Метод: получить одну заметку по ID
    def get_note(self, note_id: str) -> Note:
        """
        Загружает и возвращает заметку по её идентификатору.

        Аргументы:
            note_id: идентификатор заметки

        Возвращает:
            Объект Note

        Вызывает:
            LookupError: если заметка не найдена
        """
        # Загружаем заметку с диска
        note = self.fs.load_note(note_id)

        # Если заметка не найдена — выбрасываем ошибку
        if note is None:
            logger.error(f"Заметка не найдена: ID {note_id}")
            raise LookupError(f"Заметка с ID '{note_id}' не найдена!")

        # Возвращаем найденную заметку
        return note

    # Метод: получить список всех заметок
    def list_notes(self) -> list:
        """
        Загружает и возвращает список всех сохранённых заметок.

        Возвращает:
            Список объектов Note (может быть пустым)
        """
        # Загружаем все заметки с диска
        notes = self.fs.load_all_notes()

        # Логируем количество найденных заметок
        logger.info(f"Получен список заметок: {len(notes)} шт.")

        # Возвращаем список
        return notes

    # Метод: поиск заметок по заголовку
    def search_notes(self, query: str) -> list:
        """
        Ищет заметки, заголовок которых содержит указанный текст.

        Аргументы:
            query: строка для поиска (регистр не важен)

        Возвращает:
            Список найденных объектов Note
        """
        # Загружаем все заметки
        all_notes = self.fs.load_all_notes()

        # Ищем заметки, заголовок которых содержит запрос (без учёта регистра)
        found_notes = [
            note for note in all_notes
            if query.lower() in note.title.lower()
        ]

        # Логируем результат поиска
        logger.info(f"Поиск по запросу '{query}': найдено {len(found_notes)} заметок")

        # Возвращаем результат
        return found_notes
