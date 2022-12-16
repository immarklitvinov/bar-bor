from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# кнопки отправки контакта и локации
markup_requests = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    KeyboardButton("Отправить свой контакт", request_contact=True))

markup_requests1 = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Поиск бара по названию")).add(
    KeyboardButton("Поиск бара по метро")).add(KeyboardButton("Куда записан пользователь")).add(
    KeyboardButton("Отмена поиска"))

markup_bar = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Показать следующий бар")).add(KeyboardButton("Отмена"))

markup_bar_1 = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Записаться в бар")).add(
    KeyboardButton("Отмена поиска"))

markup_male = InlineKeyboardMarkup(resize_keyboard=True).add(
    InlineKeyboardButton("Парень 🧑", callback_data='male')).add(
    InlineKeyboardButton("Девушка 👩", callback_data='female'))

markup_users = InlineKeyboardMarkup(resize_keyboard=True).add(
    InlineKeyboardButton("Следующий", callback_data='next')).add(
    InlineKeyboardButton("Предыдущий", callback_data='previous'))

help_message = \
'''Все команды бота
/start - начало регистрации
/profile - редактирование профиля
/regphone - отправка вашего номера телефона
/find_bar - поиск бара по названию и метро
/help - вызов справки
'''