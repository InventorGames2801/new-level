"""
Модуль с начальными данными для словаря.
Содержит 100 английских слов с переводом, описанием и уровнем сложности.
"""

INITIAL_WORDS = """
Модуль с начальными данными для словаря.
Содержит 100 английских слов с переводом, описанием и уровнем сложности.
"""

INITIAL_WORDS = """
Модуль с начальными данными для словаря.
Содержит 100 английских слов с переводом, описанием и уровнем сложности.
"""

INITIAL_WORDS = [
    # Легкие слова (40 слов)
    {
        "text": "cat",
        "translation": "кошка",
        "description": "Небольшое одомашненное плотоядное млекопитающее",
        "difficulty": "easy",
    },
    {
        "text": "dog",
        "translation": "собака",
        "description": "Одомашненное плотоядное млекопитающее, обычно с длинной мордой",
        "difficulty": "easy",
    },
    {
        "text": "house",
        "translation": "дом",
        "description": "Здание для проживания людей",
        "difficulty": "easy",
    },
    {
        "text": "car",
        "translation": "машина",
        "description": "Дорожное транспортное средство с двигателем",
        "difficulty": "easy",
    },
    {
        "text": "book",
        "translation": "книга",
        "description": "Письменное или напечатанное произведение, состоящее из страниц",
        "difficulty": "easy",
    },
    {
        "text": "tree",
        "translation": "дерево",
        "description": "Древесное многолетнее растение со стволом и ветвями",
        "difficulty": "easy",
    },
    {
        "text": "sun",
        "translation": "солнце",
        "description": "Звезда, вокруг которой вращается Земля",
        "difficulty": "easy",
    },
    {
        "text": "water",
        "translation": "вода",
        "description": "Бесцветная, прозрачная, без запаха жидкость",
        "difficulty": "easy",
    },
    {
        "text": "food",
        "translation": "еда",
        "description": "Любое питательное вещество, которое едят или пьют люди",
        "difficulty": "easy",
    },
    {
        "text": "table",
        "translation": "стол",
        "description": "Мебель с плоской столешницей и ножками",
        "difficulty": "easy",
    },
    {
        "text": "chair",
        "translation": "стул",
        "description": "Сиденье для одного человека со спинкой и четырьмя ножками",
        "difficulty": "easy",
    },
    {
        "text": "door",
        "translation": "дверь",
        "description": "Дверь на петлях, закрывающая проход",
        "difficulty": "easy",
    },
    {
        "text": "window",
        "translation": "окно",
        "description": "Отверстие в стене или крыше для поступления света и воздуха",
        "difficulty": "easy",
    },
    {
        "text": "friend",
        "translation": "друг",
        "description": "Человек, которого знаешь и к которому хорошо относишься",
        "difficulty": "easy",
    },
    {
        "text": "mother",
        "translation": "мать",
        "description": "Женщина-родитель",
        "difficulty": "easy",
    },
    {
        "text": "father",
        "translation": "отец",
        "description": "Мужчина-родитель",
        "difficulty": "easy",
    },
    {
        "text": "child",
        "translation": "ребенок",
        "description": "Человек до наступления половой зрелости",
        "difficulty": "easy",
    },
    {
        "text": "school",
        "translation": "школа",
        "description": "Учебное заведение для детей",
        "difficulty": "easy",
    },
    {
        "text": "pen",
        "translation": "ручка",
        "description": "Прибор для письма или рисования чернилами",
        "difficulty": "easy",
    },
    {
        "text": "phone",
        "translation": "телефон",
        "description": "Устройство для общения на расстоянии",
        "difficulty": "easy",
    },
    {
        "text": "time",
        "translation": "время",
        "description": "Бесконечное течение существования и событий",
        "difficulty": "easy",
    },
    {
        "text": "day",
        "translation": "день",
        "description": "Период в 24 часа",
        "difficulty": "easy",
    },
    {
        "text": "night",
        "translation": "ночь",
        "description": "Время от заката до рассвета",
        "difficulty": "easy",
    },
    {
        "text": "year",
        "translation": "год",
        "description": "Время, за которое Земля совершает оборот вокруг Солнца",
        "difficulty": "easy",
    },
    {
        "text": "hand",
        "translation": "рука",
        "description": "Конечная часть руки за запястьем",
        "difficulty": "easy",
    },
    {
        "text": "eye",
        "translation": "глаз",
        "description": "Орган зрения",
        "difficulty": "easy",
    },
    {
        "text": "head",
        "translation": "голова",
        "description": "Верхняя часть тела, где находится мозг",
        "difficulty": "easy",
    },
    {
        "text": "foot",
        "translation": "нога",
        "description": "Нижняя часть ноги ниже лодыжки",
        "difficulty": "easy",
    },
    {
        "text": "heart",
        "translation": "сердце",
        "description": "Орган, перекачивающий кровь по телу",
        "difficulty": "easy",
    },
    {
        "text": "boy",
        "translation": "мальчик",
        "description": "Мальчик или молодой мужчина",
        "difficulty": "easy",
    },
    {
        "text": "girl",
        "translation": "девочка",
        "description": "Девочка или молодая женщина",
        "difficulty": "easy",
    },
    {
        "text": "man",
        "translation": "мужчина",
        "description": "Взрослый мужчина",
        "difficulty": "easy",
    },
    {
        "text": "woman",
        "translation": "женщина",
        "description": "Взрослая женщина",
        "difficulty": "easy",
    },
    {
        "text": "apple",
        "translation": "яблоко",
        "description": "Круглый плод дерева, обычно красного, желтого или зеленого цвета",
        "difficulty": "easy",
    },
    {
        "text": "bread",
        "translation": "хлеб",
        "description": "Еда из муки, воды и дрожжей, испеченная в духовке",
        "difficulty": "easy",
    },
    {
        "text": "milk",
        "translation": "молоко",
        "description": "Белая жидкость, производимая самками млекопитающих",
        "difficulty": "easy",
    },
    {
        "text": "fish",
        "translation": "рыба",
        "description": "Холоднокровное позвоночное животное, живущее в воде",
        "difficulty": "easy",
    },
    {
        "text": "bird",
        "translation": "птица",
        "description": "Теплокровное позвоночное с крыльями, перьями и клювом, откладывающее яйца",
        "difficulty": "easy",
    },
    {
        "text": "sky",
        "translation": "небо",
        "description": "Часть атмосферы, видимая с Земли",
        "difficulty": "easy",
    },
    {
        "text": "star",
        "translation": "звезда",
        "description": "Яркая точка на ночном небе",
        "difficulty": "easy",
    },
    # Средние слова (30 слов)
    {
        "text": "adventure",
        "translation": "приключение",
        "description": "Необычный и захватывающий опыт или деятельность",
        "difficulty": "medium",
    },
    {
        "text": "important",
        "translation": "важный",
        "description": "Обладающий большой значимостью или ценностью",
        "difficulty": "medium",
    },
    {
        "text": "beautiful",
        "translation": "красивый",
        "description": "Эстетически приятный для чувств или разума",
        "difficulty": "medium",
    },
    {
        "text": "difficult",
        "translation": "трудный",
        "description": "Требующий много усилий или умений для выполнения",
        "difficulty": "medium",
    },
    {
        "text": "knowledge",
        "translation": "знание",
        "description": "Факты, информация и умения, приобретённые через опыт или обучение",
        "difficulty": "medium",
    },
    {
        "text": "question",
        "translation": "вопрос",
        "description": "Предложение, сформулированное для получения информации",
        "difficulty": "medium",
    },
    {
        "text": "answer",
        "translation": "ответ",
        "description": "Ответ на вопрос",
        "difficulty": "medium",
    },
    {
        "text": "problem",
        "translation": "проблема",
        "description": "Ситуация или вопрос, считающиеся нежелательными или вредными",
        "difficulty": "medium",
    },
    {
        "text": "solution",
        "translation": "решение",
        "description": "Способ решения проблемы или сложной ситуации",
        "difficulty": "medium",
    },
    {
        "text": "journey",
        "translation": "путешествие",
        "description": "Действие по перемещению из одного места в другое",
        "difficulty": "medium",
    },
    {
        "text": "experience",
        "translation": "опыт",
        "description": "Практический контакт с фактами или событиями и их наблюдение",
        "difficulty": "medium",
    },
    {
        "text": "situation",
        "translation": "ситуация",
        "description": "Совокупность обстоятельств, в которых кто-либо оказывается",
        "difficulty": "medium",
    },
    {
        "text": "opportunity",
        "translation": "возможность",
        "description": "Совокупность обстоятельств, позволяющих что-либо сделать",
        "difficulty": "medium",
    },
    {
        "text": "understand",
        "translation": "понимать",
        "description": "Понимать предполагаемый смысл слов или действий",
        "difficulty": "medium",
    },
    {
        "text": "continue",
        "translation": "продолжать",
        "description": "Продолжать какую-либо деятельность или процесс",
        "difficulty": "medium",
    },
    {
        "text": "consider",
        "translation": "рассматривать",
        "description": "Обдумывать что-либо внимательно",
        "difficulty": "medium",
    },
    {
        "text": "successful",
        "translation": "успешный",
        "description": "Достигающий желаемой цели или результата",
        "difficulty": "medium",
    },
    {
        "text": "different",
        "translation": "различный",
        "description": "Не такой, как другой или другие",
        "difficulty": "medium",
    },
    {
        "text": "language",
        "translation": "язык",
        "description": "Способ человеческого общения — устный или письменный",
        "difficulty": "medium",
    },
    {
        "text": "education",
        "translation": "образование",
        "description": "Процесс получения или предоставления систематических знаний",
        "difficulty": "medium",
    },
    {
        "text": "business",
        "translation": "бизнес",
        "description": "Занятие коммерцией для заработка на жизнь",
        "difficulty": "medium",
    },
    {
        "text": "government",
        "translation": "правительство",
        "description": "Группа людей, обладающих властью управлять страной",
        "difficulty": "medium",
    },
    {
        "text": "computer",
        "translation": "компьютер",
        "description": "Электронное устройство для хранения и обработки данных",
        "difficulty": "medium",
    },
    {
        "text": "internet",
        "translation": "интернет",
        "description": "Глобальная компьютерная сеть для передачи информации и общения",
        "difficulty": "medium",
    },
    {
        "text": "technology",
        "translation": "технология",
        "description": "Применение научных знаний на практике",
        "difficulty": "medium",
    },
    {
        "text": "direction",
        "translation": "направление",
        "description": "Путь, по которому кто-то или что-то движется",
        "difficulty": "medium",
    },
    {
        "text": "necessary",
        "translation": "необходимый",
        "description": "Требующийся для выполнения, достижения или наличия",
        "difficulty": "medium",
    },
    {
        "text": "remember",
        "translation": "помнить",
        "description": "Держать в памяти или вспоминать о ком-либо или чем-либо",
        "difficulty": "medium",
    },
    {
        "text": "decision",
        "translation": "решение",
        "description": "Заключение или вывод после обдумывания",
        "difficulty": "medium",
    },
    {
        "text": "research",
        "translation": "исследование",
        "description": "Систематическое изучение материалов и источников",
        "difficulty": "medium",
    },
    # Сложные слова (30 слов)
    {
        "text": "acknowledge",
        "translation": "признавать",
        "description": "Принимать или признавать существование или истинность чего-либо",
        "difficulty": "hard",
    },
    {
        "text": "extraordinary",
        "translation": "необычный",
        "description": "Очень необычный или выдающийся",
        "difficulty": "hard",
    },
    {
        "text": "sophisticated",
        "translation": "сложный",
        "description": "Обладающий большим жизненным опытом или знанием",
        "difficulty": "hard",
    },
    {
        "text": "comprehensive",
        "translation": "всесторонний",
        "description": "Включающий или охватывающий все или почти все элементы или аспекты чего-либо",
        "difficulty": "hard",
    },
    {
        "text": "determination",
        "translation": "решимость",
        "description": "Качество быть решительным; твердость цели",
        "difficulty": "hard",
    },
    {
        "text": "overwhelming",
        "translation": "подавляющий",
        "description": "Очень большой по объему, эффекту или силе",
        "difficulty": "hard",
    },
    {
        "text": "nevertheless",
        "translation": "тем не менее",
        "description": "Несмотря на это; всё равно; однако",
        "difficulty": "hard",
    },
    {
        "text": "deliberately",
        "translation": "преднамеренно",
        "description": "Сознательно и намеренно; специально",
        "difficulty": "hard",
    },
    {
        "text": "enthusiasm",
        "translation": "энтузиазм",
        "description": "Сильное и живое удовольствие, интерес или одобрение",
        "difficulty": "hard",
    },
    {
        "text": "surveillance",
        "translation": "наблюдение",
        "description": "Тщательное наблюдение, особенно за подозреваемым",
        "difficulty": "hard",
    },
    {
        "text": "consequently",
        "translation": "следовательно",
        "description": "Вследствие чего-либо, как результат",
        "difficulty": "hard",
    },
    {
        "text": "rehabilitation",
        "translation": "реабилитация",
        "description": "Действия по возвращению кого-либо к здоровью или нормальной жизни",
        "difficulty": "hard",
    },
    {
        "text": "phenomenon",
        "translation": "феномен",
        "description": "Факт или ситуация, существование или возникновение которых наблюдается",
        "difficulty": "hard",
    },
    {
        "text": "entrepreneur",
        "translation": "предприниматель",
        "description": "Человек, который организует и управляет бизнесом",
        "difficulty": "hard",
    },
    {
        "text": "confidential",
        "translation": "конфиденциальный",
        "description": "Предназначенный для сохранения в тайне",
        "difficulty": "hard",
    },
    {
        "text": "occasionally",
        "translation": "иногда",
        "description": "С нечастой или нерегулярной периодичностью; время от времени",
        "difficulty": "hard",
    },
    {
        "text": "controversy",
        "translation": "противоречие",
        "description": "Затяжное публичное несогласие или ожесточенная дискуссия",
        "difficulty": "hard",
    },
    {
        "text": "circumstance",
        "translation": "обстоятельство",
        "description": "Факт или условие, связанное с событием или действием",
        "difficulty": "hard",
    },
    {
        "text": "appropriate",
        "translation": "соответствующий",
        "description": "Подходящий или надлежащий в конкретных обстоятельствах",
        "difficulty": "hard",
    },
    {
        "text": "environment",
        "translation": "окружающая среда",
        "description": "Окружение или условия, в которых живет человек, животное или растение",
        "difficulty": "hard",
    },
    {
        "text": "development",
        "translation": "развитие",
        "description": "Процесс роста или увеличения чего-либо",
        "difficulty": "hard",
    },
    {
        "text": "contribute",
        "translation": "способствовать",
        "description": "Давать что-то для достижения или обеспечения чего-либо",
        "difficulty": "hard",
    },
    {
        "text": "inspiration",
        "translation": "вдохновение",
        "description": "Процесс получения душевного подъема для действия или чувства",
        "difficulty": "hard",
    },
    {
        "text": "perspective",
        "translation": "перспектива",
        "description": "Особое отношение к чему-либо или способ восприятия",
        "difficulty": "hard",
    },
    {
        "text": "achievement",
        "translation": "достижение",
        "description": "Дело, выполненное успешно с усилиями, умением или храбростью",
        "difficulty": "hard",
    },
    {
        "text": "significant",
        "translation": "значительный",
        "description": "Достаточно великий или важный, чтобы заслуживать внимания",
        "difficulty": "hard",
    },
    {
        "text": "hypothesis",
        "translation": "гипотеза",
        "description": "Предположение или объяснение, основанное на ограниченных данных",
        "difficulty": "hard",
    },
    {
        "text": "psychology",
        "translation": "психология",
        "description": "Научное изучение человеческого разума и его функций",
        "difficulty": "hard",
    },
    {
        "text": "consciousness",
        "translation": "сознание",
        "description": "Состояние бодрствования и осознанности происходящего вокруг",
        "difficulty": "hard",
    },
    {
        "text": "particularly",
        "translation": "особенно",
        "description": "В большей степени, чем обычно или в среднем",
        "difficulty": "hard",
    },
]


def initialize_dictionary(db):
    """
    Инициализирует словарь начальными данными,
    если в базе данных еще нет слов.

    Args:
        db: Сессия базы данных SQLAlchemy

    Returns:
        int: Количество добавленных слов или 0, если словарь уже был заполнен
    """
    from app.models import Word
    from sqlalchemy import func
    from datetime import datetime, timezone

    # Проверяем, есть ли уже слова в базе
    existing_count = db.query(func.count(Word.id)).scalar() or 0

    if existing_count == 0:
        # Добавляем слова из списка
        for word_data in INITIAL_WORDS:
            word = Word(
                text=word_data["text"],
                translation=word_data["translation"],
                description=word_data["description"],
                difficulty=word_data["difficulty"],
                created_at=datetime.now(timezone.utc),
                times_shown=0,
                times_correct=0,
                correct_ratio=0.0,
            )
            db.add(word)

        db.commit()
        return len(INITIAL_WORDS)

    return 0


# Если файл запущен напрямую, выводим информацию о содержимом
if __name__ == "__main__":
    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}

    for word in INITIAL_WORDS:
        difficulty_counts[word["difficulty"]] += 1

    print(f"Общее количество слов: {len(INITIAL_WORDS)}")
    print(f"Легкие слова: {difficulty_counts['easy']}")
    print(f"Средние слова: {difficulty_counts['medium']}")
    print(f"Сложные слова: {difficulty_counts['hard']}")
