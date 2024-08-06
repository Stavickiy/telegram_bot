# iHerbDonbassBot

iHerbDonbassBot - это асинхронный чат-бот для Telegram, предназначенный для взаимодействия с пользователями интернет-магазина iHerbDonbass. Бот предоставляет информацию о категориях, брендах и продуктах, доступных в магазине, а также позволяет отправить сообщение менеджеру.

<p align="center">
  <img src="iHerbDonbassBot/media/img/1.png" alt="Описание изображения" width="300"/>
  <img src="iHerbDonbassBot/media/img/2.png" alt="Описание изображения" width="300"/>
</p>

## Установка

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/yourusername/iHerbDonbassBot.git
    cd iHerbDonbassBot
    ```

2. Создайте виртуальное окружение и активируйте его:

    ```bash
    python -m venv venv
    source venv/bin/activate  # для Windows: venv\Scripts\activate
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Создайте файл `.env` и добавьте в него необходимые переменные окружения:

    ```env
    TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    API_BASE_URL=YOUR_API_BASE_URL
    PRODUCTS_BASE_URL=YOUR_PRODUCTS_BASE_URL
    ADMIN_USER_NAME=YOUR_ADMIN_USERNAME
    ```

## Использование

Запустите бота:

```bash
python bot.py
```
Бот будет запущен и начнет обрабатывать сообщения пользователей.

