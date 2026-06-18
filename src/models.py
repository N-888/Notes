# Импортируем модуль dataclasses для создания простых классов данных
from dataclasses import dataclass, field

# Импортируем UUID для генерации уникальных идентификаторов каждой заметки
import uuid

# Импортируем datetime для работы с датой и временем создания заметки
from datetime import datetime

# Импортируем typing для аннотации типов (подсказки разработчику)
from typing import List, Optional


# Создаём класс Note — это модель одной заметки
# Декоратор @dataclass автоматически создаёт __init__, __repr__ и другие методы
@dataclass
class Note:
    """
    Модель заметки приложения Notes.

    Каждая заметка имеет:
    - уникальный идентификатор (id)
    - заголовок (title) — не может быть пустым
    - содержимое (content) — текст заметки
    - список вложений (attachments) — имена файлов
    - дату и время создания (created_at)
    - дату и время последнего изменения (updated_at)
    """

    # Уникальный идентификатор заметки — генерируется автоматически
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Заголовок заметки — обязателен для заполнения (бизнес-правило)
    title: str = ""

    # Содержимое заметки — текст, который пишет пользователь
    content: str = ""

    # Список вложений — имена прикреплённых файлов (по умолчанию пустой список)
    attachments: List[str] = field(default_factory=list)

    # Дата и время создания — заполняется автоматически при создании
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Дата и время последнего изменения — обновляется при сохранении
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Метод для обновления времени изменения заметки
    def touch(self) -> None:
        """
        Обновляет поле updated_at на текущее дату и время.
        Вызывается при каждом сохранении изменений в заметке.
        """
        # Устанавливаем текущее время в формате год-месяц-день часы:минуты:секунды
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Метод для преобразования заметки в словарь (для сохранения в JSON)
    def to_dict(self) -> dict:
        """
        Превращает объект заметки в обычный словарь Python.

        Возвращает:
            Словарь со всеми полями заметки
        """
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "attachments": self.attachments,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    # Статический метод: создаёт заметку из словаря (для загрузки из JSON)
    @staticmethod
    def from_dict(data: dict) -> "Note":
        """
        Создаёт объект Note из словаря.

        Аргументы:
            data: словарь с данными заметки (обычно из JSON-файла)

        Возвращает:
            Объект Note с заполненными полями
        """
        return Note(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            attachments=data.get("attachments", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
