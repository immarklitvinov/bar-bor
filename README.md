# Bar bot for hse advanced python course

Бот доступен по ссылке [https://t.me/bar_search_bot](https://t.me/bar_search_bot)

Так же в папке [pythonBot](pythonBot) есть файл `config.py` содержащий токен: `token = ...`

Запускается бот командой `docker-compose up --build -d`


Авторы проекта:
- Катя Северина @katrina3003
  - Работа с базами данных: users, bars, messages
  - sqlite3
- Тимур Шрамко @Tumkall
  - Логика и взаимодействие с пользователем
  - aiogram + asynco
- Марк Литвинов @marklitvinov
  - Парсинг баров и ресторанов, хостинг бота и контейнеризация
  - bs4, yandex.cloud, docker-compose
