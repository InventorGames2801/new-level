import random
import logging

# Настройка логгера
logger = logging.getLogger(__name__)


def create_scrambled_word(word, max_match_percentage=30):
    """
    Создает перемешанную версию слова с контролем процента совпадающих позиций букв.
    Полностью итеративный подход без рекурсии.

    Args:
        word (str): Исходное слово для перемешивания
        max_match_percentage (int): Максимальный допустимый процент совпадений

    Returns:
        str: Перемешанное слово
    """
    # Защита от пустого ввода
    if not word or len(word) <= 1:
        return word

    # Функция вычисления процента совпадений без вложенности
    def calc_matches(orig, scramb):
        matches = 0
        for i in range(len(orig)):
            if orig[i] == scramb[i]:
                matches += 1
        return (matches / len(orig)) * 100

    # Начальное перемешивание слова
    char_list = list(word)
    random.shuffle(char_list)
    current_result = "".join(char_list)

    # Проверяем, нужно ли дальнейшее перемешивание
    current_match = calc_matches(word, current_result)

    # Если сразу получили хороший результат, возвращаем его
    if current_match <= max_match_percentage:
        return current_result

    # Ограничение на количество попыток улучшения
    max_attempts = min(10, len(word) * 2)  # Адаптивное ограничение
    attempts = 0

    # Защита от одинаковых букв
    if len(set(word)) == 1:  # Все буквы одинаковые
        return current_result  # Невозможно перемешать

    # Основной цикл улучшения результата
    while current_match > max_match_percentage and attempts < max_attempts:
        # Находим совпадающие позиции
        matching_positions = []
        for i in range(len(word)):
            if word[i] == current_result[i]:
                matching_positions.append(i)

        # Если нет совпадений, выходим
        if not matching_positions:
            break

        # Преобразуем в список для модификации
        temp_list = list(current_result)

        # Для каждой совпадающей позиции пытаемся найти замену
        changes_made = False
        for pos in matching_positions:
            # Ищем позиции для обмена
            swap_candidates = []
            for i in range(len(temp_list)):
                if i != pos and temp_list[i] != word[i]:
                    swap_candidates.append(i)

            # Если есть кандидаты, выполняем обмен
            if swap_candidates:
                swap_pos = random.choice(swap_candidates)
                # Выполняем обмен
                temp_list[pos], temp_list[swap_pos] = (
                    temp_list[swap_pos],
                    temp_list[pos],
                )
                changes_made = True

        # Если не удалось сделать изменения, выходим
        if not changes_made:
            break

        # Обновляем результат
        new_result = "".join(temp_list)
        new_match = calc_matches(word, new_result)

        # Сохраняем только если результат улучшился
        if new_match < current_match:
            current_result = new_result
            current_match = new_match

        # Увеличиваем счетчик попыток
        attempts += 1

        # Дополнительная защита - если делаем много попыток, логируем для отладки
        if attempts > 5:
            logger.debug(
                f"Перемешивание слова '{word}' требует много попыток. "
                f"Текущий процент совпадений: {current_match:.1f}%, "
                f"попытка {attempts}/{max_attempts}"
            )

    # Финальная проверка и возврат результата
    logger.debug(
        f"Слово '{word}' перемешано в '{current_result}' "
        f"с процентом совпадений {current_match:.1f}% за {attempts} попыток"
    )

    return current_result
