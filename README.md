# avito_bot
# Sctructure of my project:
avito_book_bot/
├── bot.py                 # Главный файл запуска
├── config/
│   ├── settings.py        # Настройки проекта
│   ├── user_queries.yaml  # ТВОИ параметры поиска
│   └── model_config.yaml  # Настройки ML моделей
├── domain/
│   ├── entities.py        # Классы (Book, Price, Result)
│   └── interfaces.py      # Абстрактные классы
├── application/
│   └── services/          # Бизнес-логика
├── infrastructure/
│   ├── parsers/           # Avito парсер
│   ├── gateways/          # Telegram API
│   └── ml/                # AI модели
├── training/
│   └── data/              # Твои оценки книг
└── models/                # Сохраненные модели