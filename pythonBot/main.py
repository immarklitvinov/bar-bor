import json
import logging
from difflib import SequenceMatcher
from aiogram import Bot, Dispatcher, executor, types
from config import token
from sqlighter import SQLighter
from sqlighter1 import SQLighter1
from sqlighter2 import SQLighter2
import keyboards as kb
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InputMedia, InputMediaPhoto
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

l = 0
l1 = 0
current_user = 0
arr = []
metro_stations = []
bars_titles = []


with open('text.txt', encoding='UTF-8', errors='replace') as f:
    metro_stations = f.read() # содержимое файла
metro_stations = metro_stations.replace("'", '')
metro_stations = sorted(list(set(metro_stations.split(", "))))
metro_stations.pop()
metro_stations.pop()
metro_stations.pop()

with open('bars.txt', encoding='UTF-8', errors='replace') as f:
    bars_titles = f.read() # содержимое файла
bars_titles = bars_titles.replace("'", '')
bars_titles = sorted(list(set(bars_titles.split(', '))))



# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# инициализируем соединение с Базой Данных
db_users = SQLighter('users.db')
db_bars = SQLighter1('bars.db')
db_messages = SQLighter2('messages.db')

message_from_user = ''
list_with_bar = []
list_with_bar1 = []

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class PhoneNumber(StatesGroup):
    step_1 = State()


class Bar_Title(StatesGroup):
    step_2 = State()
    step_3 = State()


class Bar_Metro(StatesGroup):
    step_3 = State()
    step_3_1 = State()


class Bar_Metro1(StatesGroup):
    step_3_2 = State()


class Cancel(StatesGroup):
    step_4 = State()


class Bar_Next(StatesGroup):
    step_5 = State()


class Users_bar(StatesGroup):
    step_6 = State()


class User_photo(StatesGroup):
    step_reg_photo = State()


class User_age(StatesGroup):
    step_reg_age = State()


class User_male(StatesGroup):
    step_reg_male = State()
    step_reg_male1 = State()


class Bar_buttons(StatesGroup):
    step_bar_button = State()


class Profile(StatesGroup):
    profile1 = State()
    profile2 = State()
    profile3 = State()


@dp.message_handler(commands=['profile'])
async def starter(message: types.Message, state: FSMContext):
    await state.finish()
    markup_profile = InlineKeyboardMarkup(resize_keyboard=True).add(
        InlineKeyboardButton("Изменить пол", callback_data='sex')).add(
        InlineKeyboardButton("Изменить возраст", callback_data='age')).add(
        InlineKeyboardButton("Изменить фото", callback_data='photo')).add(
        InlineKeyboardButton("Закончить изменения", callback_data='cancel'))
    username = db_users.get_username(message.from_user.id)[1:]
    userphoto = db_users.get_photo(username)
    userphoto = list(userphoto[0])[0]
    userage = db_users.get_user_age(username)
    usersex = db_users.get_user_sex(username)
    userfullname = db_users.get_fullname(username)
    userfullname = list(userfullname[0])[0]
    await bot.send_photo(message.chat.id, userphoto,
                         caption=userfullname + '\n' + "Возраст: " + userage + '\n' + usersex,
                         reply_markup=markup_profile)
    await Profile.profile1.set()


# изменение пола
@dp.callback_query_handler(state=Profile.profile1)
async def callback_reg_in_bar(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'sex':
        markup_sex = InlineKeyboardMarkup(resize_keyboard=True).add(
            InlineKeyboardButton("Парень 🧑", callback_data='male')).add(
            InlineKeyboardButton("Девушка 👩", callback_data='female'))
        await call.answer('Выберите пол')
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup_sex)
    elif call.data == 'age':
        await bot.send_message(call.message.chat.id, 'Отправьте возраст')
        await Profile.profile3.set()
    elif call.data == 'photo':
        await bot.send_message(call.message.chat.id, 'Отправьте фотку')
        await Profile.profile2.set()
    elif call.data == 'male' or call.data == 'female':
        db_users.add_user_male(call.from_user.id, call.data)
        await call.answer('Пол успешно изменен')
        username = db_users.get_username(call.from_user.id)[1:]
        userphoto = db_users.get_photo(username)
        userphoto = list(userphoto[0])[0]
        userage = db_users.get_user_age(username)
        usersex = db_users.get_user_sex(username)
        userfullname = db_users.get_fullname(username)
        userfullname = list(userfullname[0])[0]
        markup_profile = InlineKeyboardMarkup(resize_keyboard=True).add(
            InlineKeyboardButton("Изменить пол", callback_data='sex')).add(
            InlineKeyboardButton("Изменить возраст", callback_data='age')).add(
            InlineKeyboardButton("Изменить фото", callback_data='photo')).add(
            InlineKeyboardButton("Закончить изменения", callback_data='cancel'))
        await bot.edit_message_caption(call.message.chat.id, call.message.message_id,
                                       caption=userfullname + '\n' + "Возраст: " + userage + '\n' + usersex,
                                       reply_markup=markup_profile)
    elif call.data == 'cancel':
        await bot.send_message(call.message.chat.id, 'Анкета успешно изменена')
        await state.finish()
    await bot.answer_callback_query(call.id)


@dp.message_handler(state=Profile.profile2, content_types=types.ContentTypes.PHOTO)
async def reg_new_photo(message: types.Message, state: FSMContext):
    photo = message.photo[0].file_id
    db_users.add_user_photo(message.from_user.id, photo)
    await message.answer('Фоточка обновлена')
    await state.finish()
    markup_profile = InlineKeyboardMarkup(resize_keyboard=True).add(
        InlineKeyboardButton("Изменить пол", callback_data='sex')).add(
        InlineKeyboardButton("Изменить возраст", callback_data='age')).add(
        InlineKeyboardButton("Изменить фото", callback_data='photo')).add(
        InlineKeyboardButton("Закончить изменения", callback_data='cancel'))
    username = db_users.get_username(message.from_user.id)[1:]
    userphoto = db_users.get_photo(username)
    userphoto = list(userphoto[0])[0]
    userage = db_users.get_user_age(username)
    usersex = db_users.get_user_sex(username)
    userfullname = db_users.get_fullname(username)
    userfullname = list(userfullname[0])[0]
    await bot.send_photo(message.chat.id, userphoto,
                         caption=userfullname + '\n' + "Возраст: " + userage + '\n' + usersex,
                         reply_markup=markup_profile)
    await Profile.profile1.set()


@dp.message_handler(state=Profile.profile3, content_types=types.ContentTypes.TEXT)
async def reg_new_age(message: types.Message, state: FSMContext):
    await state.finish()
    age = message.text
    t = True
    for i in range(len(age)):
        if not (age[i] >= '0' and age[i] <= '9'):
            t = False
    if not t:
        await message.answer('Отправьте корректный возраст')
        await state.finish()
        await Profile.profile3.set()
    else:
        if int(age) < 18:
            await message.answer('Вы слишком юны!\nВведите возраст заново')
            await state.finish()
            await Profile.profile3.set()
        elif int(age) > 60:
            await message.answer('В вашем возрасте бы пить чаёк\nВведите возраст заново')
            await state.finish()
            await Profile.profile3.set()
        else:
            db_users.add_user_age(message.from_user.id, age)
            await state.finish()
            markup_profile = InlineKeyboardMarkup(resize_keyboard=True).add(
                InlineKeyboardButton("Изменить пол", callback_data='sex')).add(
                InlineKeyboardButton("Изменить возраст", callback_data='age')).add(
                InlineKeyboardButton("Изменить фото", callback_data='photo')).add(
                InlineKeyboardButton("Закончить изменения", callback_data='cancel'))
            username = db_users.get_username(message.from_user.id)[1:]
            userphoto = db_users.get_photo(username)
            userphoto = list(userphoto[0])[0]
            userage = db_users.get_user_age(username)
            usersex = db_users.get_user_sex(username)
            userfullname = db_users.get_fullname(username)
            userfullname = list(userfullname[0])[0]
            await bot.send_photo(message.chat.id, userphoto,
                                 caption=userfullname + '\n' + "Возраст: " + userage + '\n' + usersex,
                                 reply_markup=markup_profile)
            await Profile.profile1.set()


@dp.message_handler(commands=['help'])
async def starter(message: types.Message):
    await message.answer(kb.help_message)


# обработка кнопок при баре (по названию)
@dp.callback_query_handler(state=Bar_Title.step_2)
async def callback_reg_in_bar(call: types.CallbackQuery):
    global current_user, arr
    if call.data[0:4] != 'next' and call.data[0:8] != 'previous':
        # если нажали записаться
        if call.data[-1] == '1':
            if db_bars.get_reg_in_bar(call.data[0:-1], db_users.get_username(call.from_user.id)) == -1:
                if db_users.users_bar(call.from_user.id)[2:-3] != "''" and db_users.users_bar(call.from_user.id)[
                                                                           2:-3] != "None":
                    db_bars.update_bar_no_user(db_users.users_bar(call.from_user.id)[2:-3],
                                               db_bars.clear_user_in_bar(db_users.users_bar(call.from_user.id)[2:-3],
                                                                         db_users.get_username(call.from_user.id)))
                    await call.answer('Вы идете в бар!\nЗапись в другой бар удалена')
                else:
                    await call.answer('Вы идете в бар')
                db_bars.into_bar(call.data[0:-1], bar_users=db_users.get_username(call.from_user.id) + ' ')
                db_users.update_regged_bar(call.from_user.id, call.data[0:-1])
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Вы уже записаны')
                await bot.answer_callback_query(call.id)
        else:
            # нажали посмотреть записавшихся
            if call.data[-1] != '0':
                people = db_bars.who_is_in_bar(call.data[0:-1])
                arr = people.strip().split()
                user_name = arr[0][1:]
                user_photo = db_users.get_photo(user_name)
                user_photo = list(user_photo[0])[0]
                user_sex = db_users.get_user_sex(user_name)
                user_age = db_users.get_user_age(user_name)
                user_phone = db_users.get_phone1(user_name)
                await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                    reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(
                                                        InlineKeyboardButton("Записаться в бар",
                                                                             callback_data=call.data[
                                                                                           0:-1] + '1')))
                markup_users = InlineKeyboardMarkup(resize_keyboard=True).add(
                    InlineKeyboardButton("Следующий", callback_data='next' + call.data[0:-1])).add(
                    InlineKeyboardButton("Предыдущий", callback_data='previous' + call.data[0:-1]))
                await bot.send_photo(call.message.chat.id, user_photo,
                                     '@' + user_name + '\n\n' + user_sex + ', ' + user_age + '\n\n' + 'Телефон: ' + user_phone,
                                     reply_markup=markup_users)
                db_messages.add_message(call.from_user.id, call.data[0:-1], people, 0)
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Нет записавшихся')
                await bot.answer_callback_query(call.id)
            await bot.answer_callback_query(call.id)
    else:
        if call.data[0:4] == 'next':
            current_user = db_messages.get_current_user(call.from_user.id, call.data[4:])
            current_user = str(current_user)
            current_user = int(current_user[2:-3])
            arr = db_messages.get_people(call.from_user.id, call.data[4:])
            arr = arr[0]
            arr = str(arr)
            arr = arr[2: -3]
            arr = arr.split()
            if current_user + 1 < len(arr):
                db_messages.set_new_people(current_user + 1, call.from_user.id, call.data[4:])
                current_user = db_messages.get_current_user(call.from_user.id, call.data[4:])
                current_user = str(current_user)
                current_user = int(current_user[2:-3])
                user_name = arr[current_user][1:]
                user_photo = db_users.get_photo(user_name)
                user_photo = list(user_photo[0])[0]
                user_phone = db_users.get_phone1(user_name)
                user_sex = db_users.get_user_sex(user_name)
                user_age = db_users.get_user_age(user_name)
                markup_users = InlineKeyboardMarkup(resize_keyboard=True).add(
                    InlineKeyboardButton("Следующий", callback_data='next' + call.data[4:])).add(
                    InlineKeyboardButton("Предыдущий", callback_data='previous' + call.data[4:]))
                await bot.edit_message_media(InputMediaPhoto(user_photo), call.message.chat.id, call.message.message_id)
                await bot.edit_message_caption(call.message.chat.id, call.message.message_id,
                                               caption='@' + user_name + '\n\n' + user_sex + ', ' + user_age + '\n\nТелефон: ' + user_phone,
                                               reply_markup=markup_users)
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Больше никто не записан')
                await bot.answer_callback_query(call.id)
            await bot.answer_callback_query(call.id)
        else:
            current_user = db_messages.get_current_user(call.from_user.id, call.data[8:])
            current_user = str(current_user)
            current_user = int(current_user[2:-3])
            arr = db_messages.get_people(call.from_user.id, call.data[8:])
            arr = arr[0]
            arr = str(arr)
            arr = arr[2: -3]
            arr = arr.split()
            if current_user - 1 > -1:
                current_user -= 1
                db_messages.set_new_people(current_user, call.from_user.id, call.data[8:])
                user_name = arr[current_user][1:]
                user_photo = db_users.get_photo(user_name)
                user_photo = list(user_photo[0])[0]
                user_sex = db_users.get_user_sex(user_name)
                user_age = db_users.get_user_age(user_name)
                user_phone = db_users.get_phone1(user_name)
                markup_users = InlineKeyboardMarkup(resize_keyboard=True).add(
                    InlineKeyboardButton("Следующий", callback_data='next' + call.data[8:])).add(
                    InlineKeyboardButton("Предыдущий", callback_data='previous' + call.data[8:]))
                await bot.edit_message_media(InputMediaPhoto(user_photo), call.message.chat.id, call.message.message_id)
                await bot.edit_message_caption(call.message.chat.id, call.message.message_id,
                                               caption='@' + user_name + '\n\n' + user_sex + ', ' + user_age + '\n\nТелефон: ' + user_phone,
                                               reply_markup=markup_users)
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Этот пользователь первый')
                await bot.answer_callback_query(call.id)
            await bot.answer_callback_query(call.id)


# запись пола
@dp.callback_query_handler(text="male")
async def callback_male(call: types.CallbackQuery):
    db_users.add_user_male(call.from_user.id, call.data)
    await call.message.answer('Еще чуть-чуть\nСколько вам лет?')
    await User_age.step_reg_age.set()
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(text="female")
async def callback_female(call: types.CallbackQuery):
    db_users.add_user_male(call.from_user.id, call.data)
    await call.message.answer('Еще чуть-чуть\nСколько вам лет?')
    await User_age.step_reg_age.set()
    await bot.answer_callback_query(call.id)


# запись возраста
@dp.message_handler(state=User_age.step_reg_age, content_types=types.ContentTypes.TEXT)
async def reg_age(message: types.Message, state: FSMContext):
    age = message.text
    t = True
    for i in range(len(age)):
        if not (age[i] >= '0' and age[i] <= '9'):
            t = False
    if not t:
        await message.answer('Отправьте корректный возраст')
        await state.finish()
        await User_age.step_reg_age.set()
    else:
        if int(age) < 18:
            await message.answer('Вы слишком юны!\nВведите возраст заново')
            await state.finish()
            await User_age.step_reg_age.set()
        elif int(age) > 60:
            await message.answer('В вашем возрасте бы пить чаёк\nВведите возраст заново')
            await state.finish()
            await User_age.step_reg_age.set()
        else:
            db_users.add_user_age(message.from_user.id, age)
            await message.answer('Осталось отправить фото')
            await User_photo.step_reg_photo.set()


# загрузка фото
@dp.message_handler(state=User_photo.step_reg_photo, content_types=types.ContentTypes.PHOTO)
async def reg_photo(message: types.Message, state: FSMContext):
    await state.finish()
    photo = message.photo[0].file_id
    # await bot.send_photo(message.chat.id, message.photo[0].file_id, caption=message.caption)
    db_users.add_user_photo(message.from_user.id, photo)
    await message.answer('Регистрация завершена!', reply_markup=kb.markup_requests1)
    await Cancel.step_4.set()


# команда регистрации пользователя
@dp.message_handler(commands=['start'])
async def registration(message: types.Message):
    if not db_users.subscriber_exists(message.from_user.id):
        # если не зарегистрирован
        db_users.add_subscriber(message.from_user.id, True, message.from_user.full_name, message.from_user.username,
                                '?')
    else:
        # обновляем, если нет телефона
        if db_users.get_phone(message.from_user.id) == '?':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username,
                                         '?')
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username,
                                         db_users.get_phone(message.from_user.id))
    await message.answer("Поехали, укажите пол", reply_markup=kb.markup_male)
    if str(message.from_user.username) == 'None':
        if db_users.get_phone(message.from_user.id) == '?':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''), '?')
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''),
                                         db_users.get_phone(message.from_user.id))
    else:
        if db_users.get_phone(message.from_user.id) == '?':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, '?')
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, db_users.get_phone(message.from_user.id))


# начинаем запись телефона
@dp.message_handler(commands=['regphone'])
async def reg_phone(message: types.Message):
    await message.answer('Поделиться телефоном ☎', reply_markup=kb.markup_requests)
    await PhoneNumber.step_1.set()


# после присланного номера записываем
@dp.message_handler(state=PhoneNumber.step_1, content_types=types.ContentTypes.CONTACT)
async def get_phonenumber(message: types.Message, state: FSMContext):
    user_phone_number = message.contact.phone_number
    if not db_users.subscriber_exists(message.from_user.id):
        # если не зарегистрирован
        db_users.add_subscriber(message.from_user.id, True, message.from_user.full_name, message.from_user.username,
                                user_phone_number)
        if str(message.from_user.username) == 'None':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''),
                                         user_phone_number)
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, user_phone_number)
    else:
        if str(message.from_user.username) == 'None':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''),
                                         user_phone_number)
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, user_phone_number)
    await message.answer('Телефон успешно зарегистрирован', reply_markup=kb.markup_requests1)
    await state.finish()
    await Cancel.step_4.set()


@dp.message_handler(state=PhoneNumber.step_1)
async def get_phonenumber1(message: types.Message, state: FSMContext):
    await message.answer('Телефон не отправлен!\nНу и ладно\nНачнем поиск баров!', reply_markup=kb.markup_requests1)
    await state.finish()
    await Cancel.step_4.set()


# поиск бара
@dp.message_handler(commands=['find_bar'])
async def registration(message: types.Message):
    await message.answer("Поиск баров", reply_markup=kb.markup_requests1)
    await Cancel.step_4.set()


# написана ерунда
@dp.message_handler(state=Cancel.step_4)
async def get_bars_from_title(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text != 'Поиск бара по названию' and message.text != 'Отмена поиска' and message.text != 'Поиск бара по метро' and message.text != 'Куда записан пользователь':
        await message.answer('Ни одна кнопка не нажата', reply_markup=kb.ReplyKeyboardRemove())
        db_messages.deleter(message.from_user.id)
    else:
        if message.text == 'Поиск бара по названию':
            await message.answer('Введи название бара', reply_markup=kb.ReplyKeyboardRemove())
            db_messages.deleter(message.from_user.id)
            await Bar_Title.step_2.set()
        elif message.text == 'Поиск бара по метро':
            await message.answer('Введи станцию метро', reply_markup=kb.ReplyKeyboardRemove())
            db_messages.deleter(message.from_user.id)
            await Bar_Metro.step_3.set()
        elif message.text == 'Куда записан пользователь':
            await message.answer('Введите хэндл', reply_markup=kb.ReplyKeyboardRemove())
            await Users_bar.step_6.set()
        elif message.text == 'Отмена поиска':
            db_messages.deleter(message.from_user.id)
            await message.answer('Поиск отменен', reply_markup=kb.ReplyKeyboardRemove())


# поиск по пользователю
@dp.message_handler(state=Users_bar.step_6)
async def search_user_bar(message: types.Message, state: FSMContext):
    if message.text[0] == '@':
        username_to_find = message.text[1:]
    else:
        username_to_find = message.text
    t = db_users.users_bar_to_go(username_to_find)
    if t != 'no_user':
        if t != "''":
            bar = db_bars.bar_title_from_bar_id(t)
            if len(bar) != 0:
                bar = list(bar[0])
                bar2 = f"<b>{bar[0]}</b>\n\n" \
                       f"{bar[1]}\n\n" \
                       f"Метро: {bar[2]}\n\n" \
                       f"{bar[3]}\n"
                await message.answer(bar2, reply_markup=kb.markup_requests1)
        else:
            await message.answer('Пользователь никуда не записан', reply_markup=kb.markup_requests1)
    else:
        await message.answer('Пользователя не существует', reply_markup=kb.markup_requests1)
    db_messages.deleter(message.from_user.id)
    await state.finish()
    await Cancel.step_4.set()


# поиск запущен по названию
@dp.message_handler(Text(equals='Отмена'), state=Bar_Title.step_2)
async def cancel_search_title(message: types.Message, state: FSMContext):
    await message.answer('Поиск по названию отменен', reply_markup=kb.markup_requests1)
    l1 = 0
    db_users.set_l1(l1, message.from_user.id)
    db_messages.deleter(message.from_user.id)
    await state.finish()
    await Cancel.step_4.set()


@dp.message_handler(state=Bar_Title.step_2)
async def get_bars_from_title(message: types.Message, state: FSMContext):
    global list_with_bar1
    l1 = list(db_users.get_l1(message.from_user.id)[0])[0]
    if l1 == 0:
        message_from_user = message.text
        index = 0
        m_val = 0
        bars_titles.sort(key=lambda s: similar(s, message_from_user), reverse=True)
        bar_name = bars_titles[0]
        list_with_bar1 = db_bars.get_bar_from_title(bar_name)
        list_with_bar1 = list(list_with_bar1)
        if len(list_with_bar1) != 0:
            list_with_bar2 = list(list_with_bar1[l1])
            await message.answer(f"Всего баров найдено: {len(list_with_bar1)}", reply_markup=kb.markup_bar)
            bar = f"<b>{list_with_bar2[0]}</b>\n\n" \
                  f"{list_with_bar2[1]}\n\n" \
                  f"Метро: {list_with_bar2[2]}\n\n" \
                  f"{list_with_bar2[3]}\n"
            l1 += 1
            db_users.set_l1(l1, message.from_user.id)
            bar_id_keyboard = str(list_with_bar2[5])
            bar_users_keyboard = str(list_with_bar2[4])
            if bar_users_keyboard == '':
                bar_users_keyboard = bar_id_keyboard + '0'
            else:
                bar_users_keyboard = bar_id_keyboard + '2'
            markup_bar = InlineKeyboardMarkup(resize_keyboard=True).add(
                InlineKeyboardButton("Записаться в бар", callback_data=bar_id_keyboard + '1')).add(
                InlineKeyboardButton("Посмотреть записавшихся", callback_data=bar_users_keyboard))
            await message.answer(bar, reply_markup=markup_bar)
        else:
            await message.answer('Бар не найден')
            l1 = 0
            db_users.set_l1(l1, message.from_user.id)
            db_messages.deleter(message.from_user.id)
            await state.finish()
    elif l1 >= 1 and message.text == 'Показать следующий бар':
        if l1 == len(list_with_bar1):
            await message.answer('Бары закончились', reply_markup=kb.ReplyKeyboardRemove())
            l1 = 0
            db_users.set_l1(l1, message.from_user.id)
            db_messages.deleter(message.from_user.id)
            await state.finish()
        else:
            list_with_bar2 = list(list_with_bar1[l1])
            bar = f"<b>{list_with_bar2[0]}</b>\n\n" \
                  f"{list_with_bar2[1]}\n\n" \
                  f"Метро: {list_with_bar2[2]}\n\n" \
                  f"{list_with_bar2[3]}\n"
            l1 += 1
            db_users.set_l1(l1, message.from_user.id)
            bar_id_keyboard = str(list_with_bar2[5])
            bar_users_keyboard = str(list_with_bar2[4])
            if bar_users_keyboard == '':
                bar_users_keyboard = bar_id_keyboard + '0'
            else:
                bar_users_keyboard = bar_id_keyboard + '2'
            markup_bar5 = InlineKeyboardMarkup(resize_keyboard=True).add(
                InlineKeyboardButton("Записаться в бар", callback_data=bar_id_keyboard + '1')).add(
                InlineKeyboardButton("Посмотреть записавшихся", callback_data=bar_users_keyboard))
            await message.answer(bar, reply_markup=markup_bar5)
    else:
        await message.answer('Процедура поиска прервана', reply_markup=kb.ReplyKeyboardRemove())
        l1 = 0
        db_users.set_l1(l1, message.from_user.id)
        db_messages.deleter(message.from_user.id)
        await state.finish()


# поиск запущен по метро
@dp.message_handler(Text(equals='Отмена'), state=Bar_Metro.step_3)
async def cancel_search(message: types.Message, state: FSMContext):
    #l = list(db_users.get_l(message.from_user.id)[0])
    #l = l[0]
    await message.answer('Поиск по метро отменен', reply_markup=kb.markup_requests1)
    db_users.set_l(0, message.from_user.id)
    db_messages.deleter(message.from_user.id)
    await state.finish()
    await Cancel.step_4.set()


# поиск запущен по метро
@dp.message_handler(state=Bar_Metro.step_3)
async def get_bars_from_metro(message: types.Message, state: FSMContext):
    global message_from_user, list_with_bar
    l = list(db_users.get_l(message.from_user.id)[0])
    l = l[0]
    if l == 0:
        message_from_user = message.text
        index = 0
        m_val = 0
        for i in range(len(metro_stations)):
            v = similar(metro_stations[i], message_from_user)
            if (m_val < v):
                m_val = v
                index = i
        message_from_user = metro_stations[index]
        list_with_bar = db_bars.get_bar_from_metro(message_from_user)
        list_with_bar = list(list_with_bar)
        if len(list_with_bar) != 0:
            list_with_bar1 = list(list_with_bar[l])
            await message.answer(f"Всего баров найдено: {len(list_with_bar)}", reply_markup=kb.markup_bar)
            bar = f"<b>{list_with_bar1[0]}</b>\n\n" \
                  f"{list_with_bar1[1]}\n\n" \
                  f"Метро: {list_with_bar1[2]}\n\n" \
                  f"{list_with_bar1[3]}\n"
            l += 1
            db_users.set_l(l, message.from_user.id)
            bar_id_keyboard = str(list_with_bar1[5])
            bar_users_keyboard = str(list_with_bar1[4])
            if bar_users_keyboard == '':
                bar_users_keyboard = bar_id_keyboard + '0'
            else:
                bar_users_keyboard = bar_id_keyboard + '2'
            markup_bar = InlineKeyboardMarkup(resize_keyboard=True).add(
                InlineKeyboardButton("Записаться в бар", callback_data=bar_id_keyboard + '1')).add(
                InlineKeyboardButton("Посмотреть записавшихся", callback_data=bar_users_keyboard))
            await message.answer(bar, reply_markup=markup_bar)
        else:
            await message.answer('Рядом баров нет')
            l = 0
            db_users.set_l(l, message.from_user.id)
            db_messages.deleter(message.from_user.id)
            await state.finish()
    elif l >= 1 and message.text == 'Показать следующий бар':
        if l == len(list_with_bar):
            await message.answer('Бары закончились', reply_markup=kb.ReplyKeyboardRemove())
            l = 0
            db_users.set_l(l, message.from_user.id)
            db_messages.deleter(message.from_user.id)
            await state.finish()
        else:
            list_with_bar1 = list(list_with_bar[l])
            bar = f"<b>{list_with_bar1[0]}</b>\n\n" \
                  f"{list_with_bar1[1]}\n\n" \
                  f"Метро: {list_with_bar1[2]}\n\n" \
                  f"{list_with_bar1[3]}\n"
            l += 1
            db_users.set_l(l, message.from_user.id)
            bar_id_keyboard = str(list_with_bar1[5])
            bar_users_keyboard = str(list_with_bar1[4])
            if bar_users_keyboard == '':
                bar_users_keyboard = bar_id_keyboard + '0'
            else:
                bar_users_keyboard = bar_id_keyboard + '2'
            markup_bar5 = InlineKeyboardMarkup(resize_keyboard=True).add(
                InlineKeyboardButton("Записаться в бар", callback_data=bar_id_keyboard + '1')).add(
                InlineKeyboardButton("Посмотреть записавшихся", callback_data=bar_users_keyboard))
            await message.answer(bar, reply_markup=markup_bar5)
    else:
        await message.answer('Процедура поиска прервана', reply_markup=kb.ReplyKeyboardRemove())
        l = 0
        db_users.set_l(l, message.from_user.id)
        db_messages.deleter(message.from_user.id)
        await state.finish()


# обработка кнопок при баре (по метро)
@dp.callback_query_handler(state=Bar_Metro.step_3)
async def callback_reg_in_bar(call: types.CallbackQuery):
    global current_user, arr
    if call.data[0:4] != 'next' and call.data[0:8] != 'previous':
        # если нажали записаться
        if call.data[-1] == '1':
            if db_bars.get_reg_in_bar(call.data[0:-1], db_users.get_username(call.from_user.id)) == -1:
                if db_users.users_bar(call.from_user.id)[2:-3] != "''" and db_users.users_bar(call.from_user.id)[
                                                                           2:-3] != "None":
                    db_bars.update_bar_no_user(db_users.users_bar(call.from_user.id)[2:-3],
                                               db_bars.clear_user_in_bar(db_users.users_bar(call.from_user.id)[2:-3],
                                                                         db_users.get_username(call.from_user.id)))
                    await call.answer('Вы идете в бар!\nЗапись в другой бар удалена')
                else:
                    await call.answer('Вы идете в бар')
                db_bars.into_bar(call.data[0:-1], bar_users=db_users.get_username(call.from_user.id) + ' ')
                db_users.update_regged_bar(call.from_user.id, call.data[0:-1])
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Вы уже записаны')
                await bot.answer_callback_query(call.id)
        else:
            # нажали посмотреть записавшихся
            if call.data[-1] != '0':
                people = db_bars.who_is_in_bar(call.data[0:-1])
                arr = people.strip().split()
                user_name = arr[0][1:]
                user_photo = db_users.get_photo(user_name)
                user_photo = list(user_photo[0])[0]
                user_sex = db_users.get_user_sex(user_name)
                user_age = db_users.get_user_age(user_name)
                user_phone = db_users.get_phone1(user_name)
                await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                                    reply_markup=InlineKeyboardMarkup(resize_keyboard=True).add(
                                                        InlineKeyboardButton("Записаться в бар",
                                                                             callback_data=call.data[
                                                                                           0:-1] + '1')))
                markup_users = InlineKeyboardMarkup(resize_keyboard=True).add(
                    InlineKeyboardButton("Следующий", callback_data='next' + call.data[0:-1])).add(
                    InlineKeyboardButton("Предыдущий", callback_data='previous' + call.data[0:-1]))
                await bot.send_photo(call.message.chat.id, user_photo,
                                     '@' + user_name + '\n\n' + user_sex + ', ' + user_age + '\n\nТелефон: ' + user_phone,
                                     reply_markup=markup_users)
                db_messages.add_message(call.from_user.id, call.data[0:-1], people, 0)
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Нет записавшихся')
                await bot.answer_callback_query(call.id)
            await bot.answer_callback_query(call.id)
    else:
        if call.data[0:4] == 'next':
            current_user = db_messages.get_current_user(call.from_user.id, call.data[4:])
            current_user = str(current_user)
            current_user = int(current_user[2:-3])
            arr = db_messages.get_people(call.from_user.id, call.data[4:])
            arr = arr[0]
            arr = str(arr)
            arr = arr[2: -3]
            arr = arr.split()
            if current_user + 1 < len(arr):
                db_messages.set_new_people(current_user + 1, call.from_user.id, call.data[4:])
                current_user = db_messages.get_current_user(call.from_user.id, call.data[4:])
                current_user = str(current_user)
                current_user = int(current_user[2:-3])
                user_name = arr[current_user][1:]
                user_photo = db_users.get_photo(user_name)
                user_photo = list(user_photo[0])[0]
                user_sex = db_users.get_user_sex(user_name)
                user_age = db_users.get_user_age(user_name)
                user_phone = db_users.get_phone1(user_name)
                markup_users = InlineKeyboardMarkup(resize_keyboard=True).add(
                    InlineKeyboardButton("Следующий", callback_data='next' + call.data[4:])).add(
                    InlineKeyboardButton("Предыдущий", callback_data='previous' + call.data[4:]))
                await bot.edit_message_media(InputMediaPhoto(user_photo), call.message.chat.id, call.message.message_id)
                await bot.edit_message_caption(call.message.chat.id, call.message.message_id,
                                               caption='@' + user_name + '\n\n' + user_sex + ', ' + user_age + '\n\nТелефон: ' + user_phone,
                                               reply_markup=markup_users)
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Больше никто не записан')
                await bot.answer_callback_query(call.id)
            await bot.answer_callback_query(call.id)
        else:
            current_user = db_messages.get_current_user(call.from_user.id, call.data[8:])
            current_user = str(current_user)
            current_user = int(current_user[2:-3])
            arr = db_messages.get_people(call.from_user.id, call.data[8:])
            arr = arr[0]
            arr = str(arr)
            arr = arr[2: -3]
            arr = arr.split()
            if current_user - 1 > -1:
                current_user -= 1
                db_messages.set_new_people(current_user, call.from_user.id, call.data[8:])
                user_name = arr[current_user][1:]
                user_photo = db_users.get_photo(user_name)
                user_photo = list(user_photo[0])[0]
                user_sex = db_users.get_user_sex(user_name)
                user_age = db_users.get_user_age(user_name)
                user_phone = db_users.get_phone1(user_name)
                markup_users = InlineKeyboardMarkup(resize_keyboard=True).add(
                    InlineKeyboardButton("Следующий", callback_data='next' + call.data[8:])).add(
                    InlineKeyboardButton("Предыдущий", callback_data='previous' + call.data[8:]))
                await bot.edit_message_media(InputMediaPhoto(user_photo), call.message.chat.id, call.message.message_id)
                await bot.edit_message_caption(call.message.chat.id, call.message.message_id,
                                               caption='@' + user_name + '\n\n' + user_sex + ', ' + user_age + '\n\nТелефон: ' + user_phone,
                                               reply_markup=markup_users)
                await bot.answer_callback_query(call.id)
            else:
                await call.answer('Этот пользователь первый')
                await bot.answer_callback_query(call.id)
            await bot.answer_callback_query(call.id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
