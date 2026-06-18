# Импортируем модуль os для очистки экрана консоли
import os

# Импортируем модуль sys для корректного завершения программы
import sys

# Импортируем бизнес-логику для работы с заметками
from src.business_logic import BusinessLogic

# Импортируем логгер для записи событий интерфейса
from src.logger import setup_logger


# Создаём логгер для модуля интерфейса
logger = setup_logger("ui")


# Создаём класс UI — пользовательский интерфейс приложения
# Все взаимодействие с пользователем происходит через этот класс
class UI:
    """
    Консольный пользовательский интерфейс приложения Notes.

    Предоставляет меню с операциями:
    1. Создать заметку
    2. Просмотреть все заметки
    3. Просмотреть одну заметку
    4. Редактировать заметку
    5. Удалить заметку
    6. Поиск заметок
    7. Выход из приложения
    """

    # Конструктор — принимает объект бизнес-логики
    def __init__(self, logic: BusinessLogic) -> None:
        """
        Инициализирует интерфейс.

        Аргументы:
            logic: объект BusinessLogic для выполнения операций с заметками
        """
        # Сохраняем ссылку на бизнес-логику
        self.logic = logic

        # Логируем создание интерфейса
        logger.info("Пользовательский интерфейс инициализирован")

    # Метод: очистить экран консоли
    def _clear_screen(self) -> None:
        """
        Очищает экран консоли для красоты.
        Работает на Windows, Linux и Mac.
        """
        # На Windows используем cls, на других системах — clear
        os.system("cls" if os.name == "nt" else "clear")

    # Метод: показать заголовок приложения
    def _show_header(self) -> None:
        """
        Печатает красивый заголовок приложения в консоли.
        """
        print()
        print("=" * 55)
        print("       📝  ЗАМЕТКИ  |  NOTES APP")
        print("=" * 55)

    # Метод: показать главное меню
    def _show_menu(self) -> None:
        """
        Печатает главное меню с вариантами действий.
        """
        print()
        print("  ┌─────────────────────────────────────────┐")
        print("  │           ГЛАВНОЕ МЕНЮ                   │")
        print("  ├─────────────────────────────────────────┤")
        print("  │  1. 📄 Создать новую заметку             │")
        print("  │  2. 📋 Просмотреть все заметки           │")
        print("  │  3. 🔍 Просмотреть одну заметку          │")
        print("  │  4. ✏️  Редактировать заметку             │")
        print("  │  5. 🗑️  Удалить заметку                  │")
        print("  │  6. 🔎 Поиск по заголовку               │")
        print("  │  7. 🚪 Выход                            │")
        print("  └─────────────────────────────────────────┘")

    # Метод: безопасно получить число от пользователя
    def _get_number(self, prompt: str, min_val: int = 1, max_val: int = 7) -> int:
        """
        Запрашивает у пользователя число и проверяет его корректность.

        Аргументы:
            prompt: текст приглашения для ввода
            min_val: минимальное допустимое значение
            max_val: максимальное допустимое значение

        Возвращает:
            Целое число в диапазоне [min_val, max_val]
        """
        while True:
            try:
                # Спрашиваем пользователя
                value = int(input(prompt))

                # Проверяем, что число в допустимом диапазоне
                if min_val <= value <= max_val:
                    return value

                # Если число вне диапазона — предупреждаем
                print(f"  ⚠️  Введите число от {min_val} до {max_val}!")

            except ValueError:
                # Если пользователь ввёл не число — предупреждаем
                print("  ⚠️  Пожалуйста, введите число!")

    # Метод: безопасно получить текст от пользователя
    def _get_text(self, prompt: str, allow_empty: bool = False) -> str:
        """
        Запрашивает у пользователя текст и проверяет, что он не пустой.

        Аргументы:
            prompt: текст приглашения для ввода
            allow_empty: разрешить ли пустой ввод (по умолчанию False)

        Возвращает:
            Введённую строку
        """
        while True:
            # Спрашиваем пользователя
            value = input(prompt).strip()

            # Если текст не пустой — возвращаем его
            if value or allow_empty:
                return value

            # Если текст пустой и пустой ввод запрещён — предупреждаем
            print("  ⚠️  Поле не может быть пустым! Введите данные.")

    # Метод: показать одну заметку красиво
    def _display_note(self, note) -> None:
        """
        Красиво печатает одну заметку в консоли.

        Аргументы:
            note: объект Note для отображения
        """
        print()
        print("  ┌─────────────────────────────────────────┐")
        print(f"  │  📌 {note.title}")
        print("  ├─────────────────────────────────────────┤")
        print(f"  │  ID: {note.id}")
        print(f"  │  Создано: {note.created_at}")
        print(f"  │  Изменено: {note.updated_at}")
        print("  ├─────────────────────────────────────────┤")

        # Если есть содержимое — показываем его
        if note.content:
            # Разбиваем текст на строки и выводим с отступом
            for line in note.content.split("\n"):
                print(f"  │  {line}")
        else:
            print("  │  (пусто)")

        print("  ├─────────────────────────────────────────┤")

        # Если есть вложения — показываем их список
        if note.attachments:
            print("  │  📎 Вложения:")
            for att in note.attachments:
                print(f"  │     - {att}")
        else:
            print("  │  📎 Вложений нет")

        print("  └─────────────────────────────────────────┘")

    # === ОПЕРАЦИИ ИЗ МЕНЮ ===

    # Операция 1: создать заметку
    def _create_note(self) -> None:
        """
        Запрашивает у пользователя данные и создаёт новую заметку.
        """
        print()
        print("  --- 📄 Создание новой заметки ---")

        # Запрашиваем заголовок (обязательное поле)
        title = self._get_text("  Заголовок: ")

        # Запрашиваем содержимое (можно оставить пустым)
        content = self._get_text("  Содержимое (Enter — пропустить): ", allow_empty=True)

        # Запрашиваем вложения через запятую
        att_str = self._get_text("  Вложения через запятую (Enter — пропустить): ", allow_empty=True)

        # Разбиваем строку вложений по запятой и убираем пробелы
        attachments = [a.strip() for a in att_str.split(",") if a.strip()] if att_str else []

        try:
            # Создаём заметку через бизнес-логику
            new_note = self.logic.create_note(title, content, attachments)

            # Показываем пользователю созданную заметку
            print()
            print("  ✅ Заметка успешно создана!")
            self._display_note(new_note)

        except (ValueError, TypeError) as e:
            # Если данные некорректны — показываем ошибку
            print(f"  ❌ Ошибка: {e}")
            logger.error(f"Ошибка создания заметки: {e}")

    # Операция 2: показать все заметки
    def _list_notes(self) -> None:
        """
        Загружает и показывает все сохранённые заметки.
        """
        print()
        print("  --- 📋 Все заметки ---")

        # Загружаем все заметки
        notes = self.logic.list_notes()

        # Если заметок нет — сообщаем об этом
        if not notes:
            print()
            print("  📭 Заметок пока нет. Создайте первую!")
            return

        # Показываем количество найденных заметок
        print(f"\n  Найдено заметок: {len(notes)}\n")

        # Перебираем и показываем каждую заметку
        for i, note in enumerate(notes, 1):
            print(f"  [{i}] {note.title} (создано: {note.created_at})")

        # Если пользователь хочет посмотреть детали — спрашиваем номер
        print()
        choice = input("  Введите номер заметки для просмотра (Enter — вернуться): ").strip()

        if choice:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(notes):
                    self._display_note(notes[idx])
                else:
                    print("  ⚠️  Неверный номер!")
            except ValueError:
                print("  ⚠️  Введите число!")

    # Операция 3: показать одну заметку по ID
    def _view_note(self) -> None:
        """
        Запрашивает ID заметки и показывает её.
        """
        print()
        print("  --- 🔍 Просмотр заметки ---")

        # Запрашиваем ID заметки
        note_id = self._get_text("  Введите ID заметки: ")

        try:
            # Загружаем заметку
            note = self.logic.get_note(note_id)

            # Показываем её
            self._display_note(note)

        except LookupError as e:
            # Если заметка не найдена — показываем ошибку
            print(f"  ❌ {e}")

    # Операция 4: редактировать заметку
    def _edit_note(self) -> None:
        """
        Позволяет пользователю отредактировать существующую заметку.
        """
        print()
        print("  --- ✏️  Редактирование заметки ---")

        # Запрашиваем ID заметки
        note_id = self._get_text("  Введите ID заметки: ")

        try:
            # Загружаем заметку, чтобы показать текущие данные
            note = self.logic.get_note(note_id)
            self._display_note(note)

            print()
            print("  Введите новые данные (Enter — оставить без изменений):")

            # Запрашиваем новый заголовок
            new_title = input(f"  Заголовок [{note.title}]: ").strip() or None

            # Запрашиваем новый текст
            new_content = input("  Содержимое: ").strip() or None

            # Запрашиваем новые вложения
            new_att_str = input("  Вложения через запятую: ").strip()

            # Если пользователь что-то ввёл — разбиваем по запятой
            new_attachments = [a.strip() for a in new_att_str.split(",") if a.strip()] if new_att_str else None

            # Обновляем заметку
            updated_note = self.logic.update_note(
                note_id,
                title=new_title,
                content=new_content,
                attachments=new_attachments,
            )

            # Показываем обновлённую заметку
            print()
            print("  ✅ Заметка обновлена!")
            self._display_note(updated_note)

        except (LookupError, ValueError) as e:
            # Если что-то пошло не так — показываем ошибку
            print(f"  ❌ Ошибка: {e}")

    # Операция 5: удалить заметку
    def _delete_note(self) -> None:
        """
        Позволяет пользователю удалить заметку по ID.
        """
        print()
        print("  --- 🗑️  Удаление заметки ---")

        # Запрашиваем ID заметки
        note_id = self._get_text("  Введите ID заметки: ")

        try:
            # Загружаем заметку, чтобы показать, что удаляем
            note = self.logic.get_note(note_id)
            self._display_note(note)

            # Спрашиваем подтверждение
            confirm = input("\n  Вы уверены? (да/нет): ").strip().lower()

            if confirm in ("да", "yes", "y", "д"):
                # Удаляем заметку
                self.logic.delete_note(note_id)
                print()
                print("  ✅ Заметка удалена!")
            else:
                print()
                print("  ↩️  Удаление отменено.")

        except LookupError as e:
            # Если заметка не найдена — показываем ошибку
            print(f"  ❌ {e}")

    # Операция 6: поиск заметок
    def _search_notes(self) -> None:
        """
        Ищет заметки по части заголовка.
        """
        print()
        print("  --- 🔎 Поиск по заголовку ---")

        # Запрашиваем поисковый запрос
        query = self._get_text("  Введите текст для поиска: ")

        # Выполняем поиск
        results = self.logic.search_notes(query)

        # Если ничего не найдено — сообщаем
        if not results:
            print()
            print("  🔍 Ничего не найдено.")
            return

        # Показываем результаты
        print(f"\n  Найдено: {len(results)} заметок\n")

        for i, note in enumerate(results, 1):
            print(f"  [{i}] {note.title} (ID: {note.id})")

    # === ГЛАВНЫЙ ЦИКЛ ПРИЛОЖЕНИЯ ===

    # Метод: запустить приложение (главный цикл)
    def run(self) -> None:
        """
        Запускает главное меню приложения.
        Работает в бесконечном цикле, пока пользователь не выберет выход.
        """
        # Очищаем экран
        self._clear_screen()

        # Показываем заголовок
        self._show_header()

        # Логируем запуск приложения
        logger.info("Приложение запущено пользователем")

        # Словарь действий: номер пункта → метод для выполнения
        actions = {
            1: self._create_note,
            2: self._list_notes,
            3: self._view_note,
            4: self._edit_note,
            5: self._delete_note,
            6: self._search_notes,
        }

        # Бесконечный цикл работы приложения
        while True:
            try:
                # Показываем меню
                self._show_menu()

                # Запрашиваем выбор пользователя
                choice = self._get_number("  Ваш выбор (1-7): ", 1, 7)

                # Если выбран пункт 7 — выходим
                if choice == 7:
                    print()
                    print("  👋 До свидания! Хорошего дня!")
                    logger.info("Приложение завершено пользователем")
                    break

                # Выполняем выбранное действие
                action = actions.get(choice)
                if action:
                    action()

                # Пауза перед следующим показом меню
                input("\n  Нажмите Enter для продолжения...")

            except KeyboardInterrupt:
                # Если пользователь нажал Ctrl+C — прощаемся и выходим
                print()
                print("  👋 Программа прервана. До свидания!")
                logger.info("Приложение прервано (Ctrl+C)")
                break

            except Exception as e:
                # Если произошла непредвиденная ошибка — логируем и продолжаем
                print(f"\n  ❌ Непредвиденная ошибка: {e}")
                logger.error(f"Непредвиденная ошибка в интерфейсе: {e}")
