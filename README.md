# Бот-рецептник для Telegram

Ищет рецепты по названию ингредиента. База — файл `recipes.json`, редактируется как обычный текст.

## Файлы
- `bot.py` — код бота
- `recipes.json` — база рецептов (добавляй свои сюда)
- `requirements.txt` — зависимости

## Шаг 1. Получить токен бота
1. В Telegram напиши [@BotFather](https://t.me/BotFather).
2. Команда `/newbot`, дай боту имя и username (должен заканчиваться на `bot`).
3. BotFather пришлёт токен вида `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxx` — сохрани его.

## Шаг 2. Проверить локально (необязательно, но полезно)
```bash
pip install -r requirements.txt
export BOT_TOKEN="твой_токен"   # на Windows: set BOT_TOKEN=твой_токен
python bot.py
```
Напиши боту в Telegram `/start`, потом название ингредиента, например «курица».

## Шаг 3. Деплой

### Вариант А — Railway.app (проще всего, бесплатного лимита хватит для старта)
1. Зарегистрируйся на [railway.app](https://railway.app) через GitHub.
2. Создай новый репозиторий на GitHub, залей туда `bot.py`, `recipes.json`, `requirements.txt`.
3. В Railway: **New Project → Deploy from GitHub repo**, выбери репозиторий.
4. В настройках проекта (Variables) добавь переменную `BOT_TOKEN` со значением токена от BotFather.
5. Railway сам определит Python-проект. Если нет — в настройках Start Command укажи:
   ```
   python bot.py
   ```
6. После деплоя бот будет работать 24/7 (polling-режим, вебхук не нужен).

### Вариант Б — свой VPS (Ubuntu), для полного контроля
1. Подключись по SSH к серверу.
2. Установи Python и git, если их нет:
   ```bash
   sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
   ```
3. Склонируй/скопируй файлы бота на сервер, например в `/opt/recipebot`.
4. Создай виртуальное окружение и поставь зависимости:
   ```bash
   cd /opt/recipebot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. Создай systemd-сервис `/etc/systemd/system/recipebot.service`:
   ```ini
   [Unit]
   Description=Recipe Telegram Bot
   After=network.target

   [Service]
   WorkingDirectory=/opt/recipebot
   Environment="BOT_TOKEN=твой_токен"
   ExecStart=/opt/recipebot/venv/bin/python bot.py
   Restart=always
   User=www-data

   [Install]
   WantedBy=multi-user.target
   ```
6. Запусти и включи автозапуск:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable recipebot
   sudo systemctl start recipebot
   sudo systemctl status recipebot   # проверить, что работает
   ```

## Как добавлять рецепты
Открой `recipes.json` и добавь новый объект в массив по образцу существующих:
```json
{
  "id": 13,
  "name": "Название блюда",
  "ingredients": ["ингредиент1", "ингредиент2"],
  "time": "30 мин",
  "servings": 4,
  "instructions": "1. Шаг первый.\n2. Шаг второй."
}
```
`id` должен быть уникальным. После изменения файла перезапусти бота (на Railway — просто задеплоить заново, на VPS — `sudo systemctl restart recipebot`).

## Что можно улучшить дальше
- Более умный поиск (учёт падежей, синонимов — например через морфологический анализатор pymorphy2).
- Категории рецептов (завтрак/обед/ужин), фильтр по времени готовки.
- Хранение рецептов в базе данных (SQLite/Postgres) вместо JSON, если база вырастет за пару сотен позиций.
- Админ-команды для добавления рецептов прямо из Telegram, без правки файла руками.
