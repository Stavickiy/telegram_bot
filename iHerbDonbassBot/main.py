import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup
import requests
import logging
import asyncio
from dotenv import load_dotenv

from iHerbDonbassBot.funcs import pluralize, split_list
from iHerbDonbassBot.data import NUMBERS, CATEGORIES

# Загрузка переменных окружения
load_dotenv()

TOKEN = os.environ.get('TOKEN', 'MY_TOKEN')
API_BASE_URL = os.environ.get('API_BASE_URL', 'MY_API_BASE_URL')
PRODUCTS_BASE_URL = os.environ.get('PRODUCTS_BASE_URL', 'MY_PRODUCTS_BASE_URL')
ADMIN_USER_NAME = os.environ.get('ADMIN_USER_NAME', 'MY_ADMIN_USER_NAME')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


def start_menu():
    """
    Создает меню с инлайн и реплай кнопками.

    Returns:
        tuple: Возвращает инлайн и реплай разметку кнопок.
    """
    inline_keyboard = [
        [InlineKeyboardButton(text="🗂️Категории", callback_data='categories'),
         InlineKeyboardButton(text="🏷️Бренды", callback_data='brands')],
    ]

    reply_keyboard = [
        [
            KeyboardButton(text="🏠Главное меню"),
            KeyboardButton(text="🌐Наш сайт", web_app=WebAppInfo(url='https://herbdonbass.ru/'))
        ],
    ]

    inline_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    reply_markup = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True)

    return inline_markup, reply_markup


async def preparation_products(callback_query, products: list) -> None:
    """
    Подготавливает информацию о продуктах для отправки пользователю.

    Args:
        callback_query (types.CallbackQuery): Callback query объект.
        products (list): Список продуктов.
    """
    for prod in products:
        try:
            final_price = f"<s>{prod['final_price']}</s>" if prod['discount'] else ''.join(
                [NUMBERS[n] for n in str(prod['final_price'])])
            sale_price = ''.join([NUMBERS[n] for n in str(prod['sale_price'])]) if prod['discount'] else ''
            product_title = f"""
                <b>{prod['title']}</b>
                {'✅ В наличии' if prod['count'] else '❌ Нет в наличии'}
                <u>Цена:</u> {final_price} {sale_price}₽
                """
            product_url = PRODUCTS_BASE_URL + prod['absolute_url']

            inline_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📩Написать менеджеру", url=f"t.me/{ADMIN_USER_NAME}")],
                [InlineKeyboardButton(text="🔍Подробнее", url=product_url)]
            ])

            if 'image_url' in prod:
                image_url = 'https://herbdonbass.ru' + prod['image_url']
                print(image_url)
                await callback_query.message.answer_photo(photo=image_url, caption=product_title, parse_mode='HTML',
                                                          reply_markup=inline_kb)
            else:
                await callback_query.message.answer(text=product_title, parse_mode='HTML', reply_markup=inline_kb)
        except Exception as e:
            print(f'Проблема с позицией {prod} \n Ошибка: {e}')

    await callback_query.answer(
        f"Найдено {len(products)} {pluralize(len(products), one='продукт', few='продукта', many='продуктов')}")


@dp.message(Command("start"))
async def start(message: types.Message):
    """
    Обработчик команды /start. Отправляет приветственное сообщение и меню.

    Args:
        message (types.Message): Объект сообщения.
    """
    inline_keyboard, reply_keyboard = start_menu()
    await message.answer_photo(photo='https://herbdonbass.ru/media/img/snapedit_1720093314558.jpg', caption='',
                               parse_mode='HTML')
    await message.answer('Добро пожаловать в наш интернет-магазин! Выберите опцию:', reply_markup=inline_keyboard)
    await message.answer(text="Вы можете найти нужные витамины открыв меню", reply_markup=reply_keyboard)


@dp.callback_query(lambda c: c.data in ['categories', 'brands'])
async def handle_main_menu(callback_query: types.CallbackQuery):
    """
    Обработчик колбэк-запросов для главного меню.

    Args:
        callback_query (types.CallbackQuery): Callback query объект.
    """
    await callback_query.message.edit_reply_markup(reply_markup=None)

    if callback_query.data == 'categories':
        response = requests.get(f"{API_BASE_URL}/categories/")
        categories = response.json()

        buttons = [InlineKeyboardButton(text=CATEGORIES[cat['name']] if cat['name'] in CATEGORIES else cat['name'],
                                        callback_data=f"category_{cat['id']}") for cat in categories]
        buttons.append(InlineKeyboardButton(text='🔙Назад', callback_data='back_to_start'))
        keyboard = InlineKeyboardMarkup(inline_keyboard=split_list(buttons))

        await callback_query.message.edit_text(text="Выберите категорию:", reply_markup=keyboard)

    elif callback_query.data == 'brands':
        response = requests.get(f"{API_BASE_URL}/brands/")
        brands = response.json()

        buttons = [
            InlineKeyboardButton(text=CATEGORIES[brand['name']] if brand['name'] in CATEGORIES else brand['name'],
                                 callback_data=f"brand_{brand['id']}") for brand in brands]
        buttons.append(InlineKeyboardButton(text='🔙Назад', callback_data='back_to_start'))
        keyboard = InlineKeyboardMarkup(inline_keyboard=split_list(buttons))

        await callback_query.message.edit_text(text="Выберите бренд:", reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.startswith('category_'))
async def handle_category(callback_query: types.CallbackQuery):
    """
    Обработчик колбэк-запросов для категорий.

    Args:
        callback_query (types.CallbackQuery): Callback query объект.
    """
    await callback_query.message.edit_reply_markup(reply_markup=None)

    category_id = callback_query.data.split('_')[1]
    response = requests.get(f"{API_BASE_URL}/categories/{category_id}/vitamins/")
    products = response.json()

    await preparation_products(callback_query, products)

    back_button = [InlineKeyboardButton(text="🔙Назад", callback_data='categories')]
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[back_button])
    await callback_query.message.answer("Действие", reply_markup=back_keyboard)


@dp.callback_query(lambda c: c.data.startswith('brand_'))
async def handle_brand(callback_query: types.CallbackQuery):
    """
    Обработчик колбэк-запросов для брендов.

    Args:
        callback_query (types.CallbackQuery): Callback query объект.
    """
    await callback_query.message.edit_reply_markup(reply_markup=None)

    brand_id = callback_query.data.split('_')[1]
    response = requests.get(f"{API_BASE_URL}/brands/{brand_id}/vitamins/")
    products = response.json()

    await preparation_products(callback_query, products)

    back_button = [InlineKeyboardButton(text="🔙Назад", callback_data='brands')]
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[back_button])
    await callback_query.message.answer("Действие", reply_markup=back_keyboard)


@dp.message(lambda message: message.text == '🏠Главное меню')
async def handle_main_menu_button(message: types.Message):
    """
    Обработчик сообщения для кнопки "🏠Главное меню".

    Args:
        message (types.Message): Объект сообщения.
    """
    try:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id - 1,
            reply_markup=None
        )
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id - 2,
            reply_markup=None
        )
    except Exception as e:
        print(f"Ошибка при удалении инлайн-кнопок из предыдущего сообщения: {e}")

    inline_keyboard, _ = start_menu()

    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)


@dp.callback_query(lambda c: c.data in ['back_to_start', 'back_to_categories', 'back_to_brands'])
async def handle_back(callback_query: types.CallbackQuery):
    """
    Обработчик колбэк-запросов для кнопок "Назад".

    Args:
        callback_query (types.CallbackQuery): Callback query объект.
    """
    await callback_query.message.edit_reply_markup(reply_markup=None)

    if callback_query.data == 'back_to_start':
        inline_keyboard, _ = start_menu()
        await callback_query.message.edit_text('Выберите опцию:', reply_markup=inline_keyboard)
    elif callback_query.data == 'back_to_categories':
        await handle_main_menu(callback_query)
    elif callback_query.data == 'back_to_brands':
        await handle_main_menu(callback_query)


async def main():
    """
    Основная функция для запуска бота.
    """
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())