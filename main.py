from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime
import os
import ssl
from aiogram.utils import executor

from sqlalchemy import Column, Integer, String, Table, ForeignKey,create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from  sqlalchemy.sql.expression import func
from telegram_bot_pagination import InlineKeyboardPaginator

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.executor import start_webhook

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
db_sheet = client.open_by_key("1a6In5Xc2eSA9PNt_ncHr6a8zbe8_33wIh8jOVje-NX4").sheet1
sold_sheet = client.open_by_key("1a6In5Xc2eSA9PNt_ncHr6a8zbe8_33wIh8jOVje-NX4").worksheets()[2]



class States(StatesGroup):
    START_STATE = State()
    # HELP_WITH_PICTURE = State()
    # HELP_WITH_PIC_NAME = State()
    # HELP_WITH_PIC_NUM = State()
    HELP_ORD_NAME = State()
    BUY_PICTURE = State()
    CHOOSE_STYLE = State()
    CHOOSE_SHADES = State()
    LIST_OF_PICTURES = State()
    CUR_PICTURE = State()
    CUR_PICTURE_CONFIRMATION = State()
    ASK_FOR_CONTACT = State()
    MANAGER_MODE = State()
    FAVOURITES = State()
    PAY_WITH_CASH = State()
    PAY_WITH_CRYPT = State()


favourites_button = KeyboardButton('Избранное ♥')
#help_button = KeyboardButton('Подберите мне картину 🖼️')
shop_button = KeyboardButton('Подобрать картину 🏪')

global_markup = ReplyKeyboardMarkup(resize_keyboard=True).insert(
    favourites_button).insert(shop_button)

inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

go_back_but = InlineKeyboardButton('Назад🔙', callback_data='go back')

markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
)

confirm_but = InlineKeyboardButton('Подтверждаю✔️', callback_data='confirmthis')

confirm_markup = InlineKeyboardMarkup().add(confirm_but)

give_choice_markup =InlineKeyboardMarkup() \
                    .insert(InlineKeyboardButton('Картой', callback_data='card')) \
                    .insert(InlineKeyboardButton('Криптой', callback_data='crypt')) \
                    .add(InlineKeyboardButton('Наличными (полная предоплата)', callback_data='cash'))

crypt_choice = InlineKeyboardMarkup()\
    .insert(InlineKeyboardButton('BTC', callback_data='btc')) \
    .insert(InlineKeyboardButton('ETH', callback_data='eth')) \
    .add(InlineKeyboardButton('USDT', callback_data='usdt'))

start_message = 'Привет! Я - Искусство, как и ты, Человек. Только бот. ' \
                'Здесь ты можешь выбрать картину на свой вкус или мои кореша-дизайнеры' \
                ' помогут подобрать самую подходящую для твоего дома картину.'

select_style = 'Выберите стиль картин'
select_style_error = 'Такого стиля нет'

select_shade = 'Предпочтения в оттенках?'
select_shade_error = 'Такого оттенка не найдено'

manager_pending = 'Наш менеджер подтверждает заказ. В скором времени появится ' \
                  'кнопка для оплаты заказа.'

successful_order = 'Спасибо за заказ! ' \
                   'В скором времени с вами свяжется наш менеджер!'

# help_pic_message = 'Ваши фото квартиры/жилого помещения (1-5 фото)'

help_message = 'Я - Искусство, как и ты, Человек. Только бот.' \
               'Здесь ты можешь выбрать картину на свой вкус или мои кореша-дизайнеры ' \
               'помогут подобрать самую подходящую для твоего дома картину. ' \
               'Для навигации используйте кнопки.'

unknown_command = 'Я вас не понимаю :(. Нажмите, пожалуйста, на кнопку.'

Base = declarative_base()

style_pic_table = Table('style_pic_table', Base.metadata,
                        Column('style_id', Integer, ForeignKey('style.id', ondelete="CASCADE")),
                        Column('picture_id', Integer, ForeignKey('picture.id', ondelete="CASCADE"))
                        )

shade_pic_table = Table('shade_pic_table', Base.metadata,
                        Column('shade_id', Integer, ForeignKey('shade.id',ondelete='CASCADE')),
                        Column('picture_id', Integer, ForeignKey('picture.id', ondelete="CASCADE"))
                        )


class Style(Base):
    __tablename__ = 'style'
    id = Column(Integer, primary_key=True)
    name = Column(String(31))

    pictures = relationship(
        'Picture',
        secondary=style_pic_table,
        back_populates='styles')


class Shade(Base):
    __tablename__ = 'shade'
    id = Column(Integer, primary_key=True)
    name = Column(String(31))
    pictures = relationship(
        'Picture',
        secondary=shade_pic_table,
        back_populates='shades')


class Picture(Base):
    __tablename__ = 'picture'
    id = Column(Integer, primary_key=True)
    name = Column(String(63))
    ph_url = Column(String(767))
    size = Column(String(127))
    author = Column(String(127))
    price = Column(Integer)
    year = Column(Integer)
    mats = Column(String(63))
    art_styles = Column(String(127))
    shades = relationship(
        'Shade',
        secondary=shade_pic_table,
        back_populates='pictures')
    styles = relationship(
        'Style',
        secondary=style_pic_table,
        back_populates='pictures')


CUR_DIV = 4500
TOKEN = '1868938472:AAFdhFMbJbrqDPcX-ytOCNhgT9Kmp2902Y0'
public_key = 'sandbox_i63619417970'
private_key = 'sandbox_wW5EUlWQAGxjR1u0exfjeqbgRgxn4LOigEediUy7'
BUY_TOKEN = '632593626:TEST:sandbox_i63619417970'
MY_ID = 344548620
DB_FILENAME = 'pictures.db'
secret_password = 'IAMART'
DB_URL = 'https://docs.google.com/spreadsheets/d/1a6In5Xc2eSA9PNt_ncHr6a8zbe8_33wIh8jOVje-NX4/gviz/tq?tqx=out:csv&sheet=Database'
MANAGER_IDS = {1586995361,
               #1942245489,
               }



host='database-1.c8pemjym32rz.us-east-2.rds.amazonaws.com'
db_name='postgres'
user='postgres'
password='Y3dWgd3AmJ08MEKTnpnX'

columns = {'name': 'Название картины',
           'styles': 'Стиль/Стили',
           'shade': 'Оттенок/Оттенки',
           'price': 'Цена',
           'size': 'Размер',
           'url': 'URL фотографии',
           'author': 'Автор',
           'mats': 'Материал/краски',
           'year': 'Написана в',
           'art_st': 'Стиль'

           }

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

WEBHOOK_HOST = 'https://deploy-heroku-bot-aiogram-pics.herokuapp.com'  # name your app
WEBHOOK_PATH = '/webhook/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.environ.get('PORT')


# GO BACK HANDLER
@dp.callback_query_handler(lambda query: query.data == 'go back', state='*')
async def handle_back_button(query, state: FSMContext):
    cur_state = await state.get_state()
    await bot.answer_callback_query(query.id)
    if str(cur_state) == States.CHOOSE_SHADES.state:
        await States.CHOOSE_STYLE.set()
        await process_callback_styles(query)
    elif str(cur_state) == States.LIST_OF_PICTURES.state:
        await States.CHOOSE_SHADES.set()
        await process_callback_shades(query)
    elif str(cur_state) == States.CHOOSE_STYLE.state:
        await States.START_STATE.set()
        await process_start_command(query.message)
    elif str(cur_state) == States.CUR_PICTURE_CONFIRMATION.state:
        await States.LIST_OF_PICTURES.set()
        async with state.proxy() as data:
            await send_character_page(query.message,data)


# CATEGORY CHOOSE HANDLER
@dp.callback_query_handler(lambda query: query.data.startswith('cat'), state='*')
async def process_callback_styles(query, state: FSMContext):
    await bot.answer_callback_query(query.id)
    await bot.delete_message(query.message.chat.id,query.message.message_id)
    async with state.proxy() as data:
        if 'favourites' not in data:
            data['favourites'] = []
        data['category'] = query.data
    await States.CHOOSE_SHADES.set()
    #session = bot.get("db")
    shades = session.query(Shade)
    shades_inline = InlineKeyboardMarkup()
    for item in shades:
        shade = InlineKeyboardButton(item.name, callback_data='sha' + str(item.id))
        shades_inline.insert(shade)
    await bot.send_message(query['from'].id, "Выберите оттенок", reply_markup=shades_inline)


# SHADE CHOOSE HANDLER
@dp.callback_query_handler(lambda query: query.data.startswith('sha'), state='*')
async def process_callback_shades(query :types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(query.id)
    await bot.delete_message(query.message.chat.id,query.message.message_id)
    async with state.proxy() as data:
        if 'favourites' not in data:
            data['favourites'] = []
        #session = bot.get("db")
        data['pictures_pagelist'] = []
        pictures_list = session.query(Picture).filter(Picture.shades.any(id=int(query.data[3:])),
                                                      Picture.styles.any(id=int(data['category'][3:])))
        await bot.send_message(query['from'].id, 'Вот ваши подобранные картины:')
        i=0
        for picture in pictures_list:
            i+=1
            data['pictures_pagelist'].append(picture)
        if i==0:
            pictures_list = session.query(Picture).order_by(func.random()).limit(20)
            for picture in pictures_list:
                data['pictures_pagelist'].append(picture)
        await send_character_page(query.message,data)

            # if 'cur_help_id' not in data:
            #     await States.LIST_OF_PICTURES.set()


# SEND INVOICE
async def send_invoice(user_id):
    user_id = int(user_id)
    state = dp.current_state(user=user_id, chat=user_id)
    async with state.proxy() as data:
        if 'exp_price' not in data:
            price = data['price']
            data['exp_price']=0
            prices_int = []
            i=0
            while price != 0:
                minus = price%CUR_DIV
                if minus != 0:
                    prices_int.append((i,minus))
                    price -= minus
                else:
                    prices_int.append((i,CUR_DIV))
                    price -= CUR_DIV
                i+=1
            data['prices_int']=prices_int
        data["ord_cur_time"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        price = data['prices_int'].pop(0)
        await bot.send_invoice(
            chat_id=user_id,
            title=f'{data["picture_name"]}',
            description=f'({price[0]+1}-ая часть оплаты)\nАвтор: {data["author"]} ',
            provider_token=BUY_TOKEN,
            currency='EUR',
            photo_url=data['photo_id'],
            photo_height=900,  # !=0/None or picture won't be shown
            photo_width=1200,
            is_flexible=False,  # True если конечная цена зависит от способа доставки
            prices=[types.LabeledPrice(label=data['picture_name'], amount=price[1]*100)],
            start_parameter='time-machine-example',
            payload=f'{user_id} {data["ord_cur_time"]}',
            need_name=True,
            need_shipping_address=True,
        )


# CHECKOUT HANDLER
@dp.pre_checkout_query_handler(lambda query: True, state='*')
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# PAYMENT FEEDBACK
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state='*')
async def process_successful_payment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['exp_price']+=message.successful_payment.total_amount//100
        #data['exp_price']+
        if data['exp_price']!=data['price']:
            await bot.send_message(message.chat.id, 'Часть оплаты прошла успешно! Следующая оплата:')
            await send_invoice(message.chat.id)
        else:
            await bot.send_message(message.chat.id, 'Оплата прошла успешно. Скоро мы с вами свяжемся!')
            order = message.successful_payment.order_info
            #session = bot.get('db')
            session.query(Picture).filter(Picture.id==["pic_id"][3:])
            #session.commit()
            for manager_id in MANAGER_IDS:
                await bot.send_message(manager_id, f'Прошла успешно оплата по картине {data["picture_name"]}\n'
                                                   f'Цена: {data["price"]} €\n'
                                                   f'Номер заказа: {message.successful_payment.invoice_payload}'
                                                   f'{data["photo_id"]}.\n'
                                                   f'Номер получателя:{data["number"]}\n'
                                                   f'Ник получателя:{message.from_user.username}\n'
                                                   f'Имя получателя (тг):{order.name}\n'
                                                   f'Страна: {order.shipping_address.country_code}\n'
                                                   f'Город: {order.shipping_address.city}\n'
                                                   f'State: {order.shipping_address.state}\n'
                                                   f'Адрес: {order.shipping_address.street_line1}\n'
                                                   f'Адрес(2): {order.shipping_address.street_line2}\n')


# manager send picture
async def manager_send_picture(user_id, pic_id, price, photo_id, picture_name, author, size):
    await bot.send_message(user_id, 'Мы подобрали вам подходящую картину')
    await bot.send_photo(chat_id=user_id, photo=photo_id, caption=f'Вы подтверждаете картину {picture_name} ?'
                                                                  f'Цена: {price} €\n',
                         reply_markup=confirm_markup.add(go_back_but))
    state = dp.current_state(chat=user_id, user=user_id)
    async with state.proxy() as data:
        data['pic_id'] = pic_id
        data['price'] = price
        data['photo_id'] = photo_id
        data['picture_name'] = picture_name
        data['author'] = author
        data['size'] = size


# PICTURE CONFIRMATION
@dp.callback_query_handler(lambda query: query.data.startswith('buy'), state='*')
async def process_callback_picture(query, state: FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['pic_id'] = query.data
        #session = bot.get("db")
        picture = session.query(Picture).filter(Picture.id==int(query.data[3:])).first()
        # if 'cur_help_id' in data:
        #     await manager_send_picture(data['cur_help_id'], picture.id, picture.price, picture.ph_url, picture.name,picture.author,picture.size)
        # else:
        await bot.send_message(query['from'].id, f'Вы подтверждаете картину ?\n')
        data['price'] = picture.price
        data['photo_id'] = picture.ph_url
        data['picture_name'] = picture.name
        data['size'] = picture.size
        data['author'] = picture.author
        await bot.send_photo(query['from'].id,
                             picture.ph_url,
                             caption=f'Ваша картина "{picture.name}"\n'
                                     f'Автор: {picture.author}\n'
                                     f'Размер: {picture.size}\n'
                                     f'Цена: {picture.price} €\n',
                             reply_markup=confirm_markup)
        await States.CUR_PICTURE_CONFIRMATION.set()


# DEL FROM FAVOURITES
@dp.callback_query_handler(lambda query: query.data.startswith('del'), state='*')
async def process_callback_rem_from_fav(query, state: FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['favourites'].remove(query.data[3:])
        added_pic_name = query.message.caption.split('\n')[0]
        if query.message.reply_markup.inline_keyboard[-1][-1]['callback_data'].startswith('cha'):
            paginator = InlineKeyboardPaginator(
                len(data['pictures_pagelist']) // 2,
                current_page=data['page'],
                data_pattern='character#{page}'
            )
            paginator.add_before(
                InlineKeyboardButton('Купить 💎', callback_data='buy' + query.data[3:]),
                InlineKeyboardButton('В избранное ♥', callback_data='fav' + query.data[3:]))
            await bot.edit_message_reply_markup(query.message.chat.id,query.message.message_id,reply_markup=paginator.markup)
        else:
            await bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id,
                                                reply_markup=InlineKeyboardMarkup().
                                                insert(InlineKeyboardButton('Купить 💎', callback_data='buy' + query.data[3:])).
                                                insert(InlineKeyboardButton('В избранное ♥', callback_data='fav' + query.data[3:])))
        await bot.send_message(query['from'].id, f'Картина {added_pic_name} успешно удалена из избранного')


# ADD TO FAVOURITES
@dp.callback_query_handler(lambda query: query.data.startswith('fav'), state='*')
async def process_callback_add_to_fav(query:types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['favourites'].append(query.data[3:])
        added_pic_name = query.message.caption.split('\n')[0]
        if query.message.reply_markup.inline_keyboard[-1][-1]['callback_data'].startswith('cha'):
            paginator = InlineKeyboardPaginator(
                len(data['pictures_pagelist']) // 2,
                current_page=data['page'],
                data_pattern='character#{page}'
            )
            paginator.add_before(
                InlineKeyboardButton('Купить 💎', callback_data='buy' + query.data[3:]),
                InlineKeyboardButton('Удалить из избранного ♥', callback_data='del' + query.data[3:]))
            await bot.edit_message_reply_markup(query.message.chat.id,query.message.message_id,reply_markup=paginator.markup)
        else:
            await bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id,
                                                reply_markup=InlineKeyboardMarkup().
                                                insert(InlineKeyboardButton('Купить 💎', callback_data='buy' + query.data[3:])).
                                                insert(InlineKeyboardButton('Удалить из избранного ♥', callback_data='del' + query.data[3:])))
        await bot.send_message(query['from'].id, f'Картина {added_pic_name} успешно добавлена в избранное')


# ASKING FOR CONTACT
@dp.callback_query_handler(lambda query: query.data == 'confirmthis', state='*')
async def process_callback_confirm(query, state: FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        if 'number' not in data:
            await bot.send_message(query['from'].id, "Нам нужен Ваш номер для связи", reply_markup=markup_request)
            await States.ASK_FOR_CONTACT.set()
        else:
            await send_confirmation_to_manager(user_id=data['user_id'],
                                               picture_name=data['picture_name'],
                                               photo_id=data['photo_id'], name=data['name'], number=data['number'])
            answer = f'{manager_pending}'
            await bot.send_message(query['from'].id, answer)



# CONTACT MANAGEMENT
@dp.message_handler(content_types=['contact'], state=States.ASK_FOR_CONTACT)
async def contact(message: types.Message, state: FSMContext):
    if message.contact is not None:
        await bot.send_message(message.chat.id, 'Вы успешно отправили свой номер', reply_markup=global_markup)
        async with state.proxy() as data:
            data['number'] = str(message.contact.phone_number)
            data['user_id'] = str(message.contact.user_id)
            if 'name' not in data:
                data['name']=str(message.contact.first_name)+str(message.contact.last_name)
            answer = f'Ваш номер:{data["number"]}\n' \
                     f'\n{manager_pending}'
            await bot.send_message(message.chat.id, answer)
            await send_confirmation_to_manager(user_id=message.from_user.id, picture_name=data['picture_name'],
                                               photo_id=data['photo_id'],name=data['name'],number=data['number'])


async def send_confirmation_to_manager(user_id, picture_name, photo_id, name, number):
    for manager_id in MANAGER_IDS:
        confirm_manager_keyboard = InlineKeyboardMarkup(). \
            insert(InlineKeyboardButton('Подтвердить',
                                        callback_data=f'm_conf,{user_id},{picture_name}')). \
            insert(InlineKeyboardButton('Нет в наличии',
                                        callback_data=f'm_disc,{user_id}'))
        await bot.send_message(manager_id, f'Заказ на картину {picture_name} {photo_id} от {name}.\nНомер: {number}',
                               reply_markup=confirm_manager_keyboard)


# manager confirm
@dp.callback_query_handler(lambda query: query.data.startswith('m_conf'), state='*')
async def managerconfirm(query):
    m_conf, user_id, picture = query.data.split(',')
    await bot.answer_callback_query(query.id)
    await bot.delete_message(query.message.chat.id,query.message.message_id)
    for manager_id in MANAGER_IDS:
        await bot.send_message(manager_id, f"Заказ на картину {picture} от {user_id} принят")
    try:
        row = db_sheet.find(picture).row
        sold = db_sheet.row_values(row)
        db_sheet.delete_rows(row)
        sold_sheet.append_row(sold)
    except:
        pass
    del_pic=session.query(Picture).filter(Picture.name==picture).first()
    session.delete(del_pic)
    session.commit()
    await bot.send_message(user_id, "Ваш заказ подтвержден")
    await give_choice_payment(user_id)
    #await send_invoice(user_id)


async def give_choice_payment(user_id):
    await bot.send_message(user_id,'Выберите способ оплаты:',reply_markup=give_choice_markup)


@dp.callback_query_handler(lambda query: query.data=='card', state='*')
async def card_handler(query:types.CallbackQuery):
    await bot.answer_callback_query(query.id)
    await send_invoice(query.from_user.id)


@dp.callback_query_handler(lambda query: query.data=='cash', state='*')
async def cash_handler(query:types.CallbackQuery):
    await bot.answer_callback_query(query.id)
    await States.PAY_WITH_CASH.set()
    await bot.send_message(query.message.chat.id,'Введите место и время (дату), когда Вам удобно передать оплату нашему курьеру')


@dp.callback_query_handler(lambda query: query.data == 'crypt', state='*')
async def crypt_handler(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id)
    await States.PAY_WITH_CRYPT.set()
    await bot.send_message(query.message.chat.id, 'Выберите криптовалюту:', reply_markup=crypt_choice)
    await manager_send_cash_info(query.message.chat.id,'Оплата криптовалютой')



BTC_T='19R1RSRDehitUUHZPA2n8uH4b3tjBmfLDN'
ETH_T='0xa7DE14Be588642a48b2191a56D4b6eBb4f0FD003'
USDT_T='0xa7DE14Be588642a48b2191a56D4b6eBb4f0FD003'
crypt_message = 'После оплаты мы свяжемся с вами'

@dp.callback_query_handler(lambda query: query.data == 'btc', state='*')
async def crypt_handler_btc(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id)
    await bot.send_message(query.message.chat.id, f'BTC Кошелек: {BTC_T}\n{crypt_message}')


@dp.callback_query_handler(lambda query: query.data == 'eth', state='*')
async def crypt_handler_eth(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id)
    await bot.send_message(query.message.chat.id, f'ETH Кошелек: {ETH_T}\n{crypt_message}')


@dp.callback_query_handler(lambda query: query.data == 'usdt', state='*')
async def crypt_handler_usdt(query: types.CallbackQuery):
    await bot.answer_callback_query(query.id)
    await bot.send_message(query.message.chat.id, f'USDT Кошелек:{USDT_T}\n{crypt_message}')


@dp.message_handler(state=States.PAY_WITH_CASH)
async def cash_answer_handler(message: types.Message):
    await bot.send_message(message.chat.id,f'Спасибо!\n'
                                           f'Вы выбрали: {message.text}\n'
                                           f'Мы свяжемся с Вами для подтверждения/уточнения деталей:)')
    await States.START_STATE.set()
    await manager_send_cash_info(message.chat.id,message.text)


async def manager_send_cash_info(user_id,adress_info):
    state = dp.current_state(user=user_id,chat=user_id)
    async with state.proxy() as data:
        answer =f'Прошла успешно оплата по картине {data["picture_name"]}\n' \
                f'Цена: {data["price"]} €\n'\
                f'{data["photo_id"]}.\n'\
                f'Номер получателя:{data["number"]}\n'\
                f'Имя получателя (тг):{data["name"]}\n' \
                f'Информация про адрес и время:{adress_info}'
        for manager_id in MANAGER_IDS:
            await bot.send_message(manager_id,answer)

# manager confirm
@dp.callback_query_handler(lambda query: query.data.startswith('m_disc'), state='*')
async def managerconfirm(query :types.CallbackQuery):
    m_disc, user_id, picture = query.data.split(',')
    await bot.answer_callback_query(query.id)
    await bot.delete_message(query.message.chat.id,query.message.message_id)
    for manager_id in MANAGER_IDS:
        await bot.send_message(manager_id, f"Заказ на картину {picture} от {user_id} отклонен")
    await bot.send_message(user_id, "К сожалению, картины нет в наличии."
                                    " Вернитесь, пожалуйста, в магазин и выберите другой вариант.")


# start message
@dp.message_handler(commands=['start'], state='*')
async def process_start_command(message: types.Message, state: FSMContext):
    await States.START_STATE.set()
    async with state.proxy() as data:
        if 'known_user' not in data:
            data['favourites'] = []
        data['known_user'] = '1'
    await message.reply(start_message, reply_markup=global_markup)


# help message
@dp.message_handler(commands=['help'],state='*')
async def process_help_command(message: types.Message):
    await message.reply(help_message, reply_markup=global_markup)


# leave manager mode
@dp.message_handler(commands=['leave_manager'], state=States.MANAGER_MODE)
async def process_leave_manager(message: types.Message):
    await States.START_STATE.set()
    MANAGER_IDS.remove(message.from_user.id)
    await message.reply('Вы в стандартном режиме', reply_markup=global_markup)


# set manager mode
@dp.message_handler(commands=['go_manager'], state='*')
async def process_go_manager(message: types.Message):
    args = message.get_args()
    if args == secret_password:
        await States.MANAGER_MODE.set()
        MANAGER_IDS.add(message.from_user.id)
        await message.reply('Выставлен режим менеджера', reply_markup=global_markup)
    else:
        await message.reply('У вас нет доступа к этой комманде', reply_markup=global_markup)


# update database
@dp.message_handler(commands=['update_db'], state='*')
async def process_update_db(message: types.Message):
    args = message.get_args()
    if args == secret_password:
        #session = bot.get('db')
        # session.execute(text('DELETE FROM shade_pic_table;'))
        # session.execute(text('DELETE FROM style_pic_table;'))
        # session.execute(text('DELETE FROM picture;'))
        # session.execute(text('DELETE FROM shade;'))
        # session.execute(text('DELETE FROM style;'))
        # session.commit()
        df = pd.read_csv(DB_URL)
        current_pics_query = session.query(Picture)
        for index, row in df.iterrows():
            cur_pic = current_pics_query.filter(Picture.name==row[columns['name']]).first()
            if cur_pic is None:
                cur_pic = Picture(name=row[columns['name']],
                                  price=row[columns['price']],
                                  ph_url=row[columns['url']],
                                  size=row[columns['size']],
                                  author=row[columns['author']],
                                  art_styles=row[columns['art_st']],
                                  mats=row[columns['mats']],
                                  year=row[columns['year']]
                                  )
            shades = row[columns['shade']].replace(" ", "").split(',')
            styles = row[columns['styles']].replace(" ", "").split(',')
            for shade in shades:
                cur_shs = session.query(Shade).filter(Shade.name==shade).first()
                if cur_shs is not None:
                    cur_pic.shades.append(cur_shs)
                else:
                    cur_pic.shades.append(Shade(name=shade))
            for style in styles:
                cur_st = session.query(Style).filter(Style.name==style).first()
                if cur_st is not None:
                    cur_pic.styles.append(cur_st)
                else:
                    cur_pic.styles.append(Style(name=style))
            session.add(cur_pic)
        session.commit()

        await message.reply('База успешно обновлена', reply_markup=global_markup)
    else:
        await message.reply('У вас нет доступа к этой комманде', reply_markup=global_markup)


async def favourites(message: types.Message, state):
    async with state.proxy() as data:
        if 'favourites' not in data:
            data['favourites'] = []
        if len(data['favourites']) > 0:
            await message.reply('Ваши любимые картины')
            await States.FAVOURITES.set()
            #session = bot.get('db')
            for picture_id in data['favourites']:
                fav_pic = InlineKeyboardMarkup() \
                    .insert(InlineKeyboardButton('Купить 💎', callback_data='buy' + str(picture_id))) \
                    .insert(InlineKeyboardButton('Удалить из избранного ♥', callback_data='del' + picture_id))
                picture = session.query(Picture).filter(Picture.id==int(picture_id)).first()

                await bot.send_photo(message.chat.id,
                                     picture.ph_url,
                                     caption=f'Ваша картина {picture.name}\n'
                                             f'Цена : {picture.price} €',
                                     reply_markup=fav_pic)
        else:
            await message.reply('У вас нет ничего :(. Перейдите в магазин, чтобы добавить картины в избранное:)')


async def shop(message: types.Message):
    #session = bot.get("db")
    styles = session.query(Style)
    styles_inline = InlineKeyboardMarkup()
    for style in styles:
        style = InlineKeyboardButton(style.name, callback_data='cat' + str(style.id))
        styles_inline.insert(style)
    await message.reply('Выберите один из нескольких стилей для вашей картины', reply_markup=styles_inline)


# async def help_with_pic(message: types.Message,state : FSMContext):
#     async with state.proxy() as data:
#         # await message.delete()
#         if 'name' not in data:
#             await bot.send_message(message.chat.id,'Как к Вам обращаться? Введите имя, пожалуйста.')
#             await States.HELP_WITH_PIC_NAME.set()
#         elif 'number' not in data:
#             await bot.send_message(message.chat.id, 'Нам нужен ваш номер для связи,'
#                                                     ' отправьте контакт, пожалуйста, используя кнопку ниже.',
#                                    reply_markup=markup_request)
#             await States.HELP_WITH_PIC_NUM.set()
#         else:
#             await bot.send_message(message.chat.id,
#                 'Мы собрали все мировые силы, чтобы подобрать картину в ваш дом и сделать его еще уютнее.'
#                 ' Отправьте нам несколько фото интерьера')




# @dp.message_handler(content_types=['photo'], state=States.HELP_WITH_PICTURE)
# async def handle_docs_photo(message: types.Message):
#     await message.reply('Спасибо. Скоро мы отправим вам несколько вариантов.')
#     suppose_keyboard = InlineKeyboardMarkup().insert(
#         InlineKeyboardButton('подобрать', callback_data=f'sup,{message.from_user.id}'))
#     for manager_id in MANAGER_IDS:
#         await message.forward(manager_id)
#         await bot.send_message(manager_id, f'Подобрать картину пользователю {message.from_user.username}',
#                                reply_markup=suppose_keyboard)


# # CONTACT MANAGEMENT
# @dp.message_handler(content_types=['contact'], state=States.HELP_WITH_PIC_NUM)
# async def contact_help(message: types.Message, state: FSMContext):
#     if message.contact is not None:
#         await bot.send_message(message.chat.id, 'Вы успешно отправили свой номер', reply_markup=global_markup)
#         async with state.proxy() as data:
#             data['number'] = str(message.contact.phone_number)
#             data['user_id'] = str(message.contact.user_id)
#             answer = f'Ваш номер: {data["number"]}'
#             await message.reply(answer)
#             await States.HELP_WITH_PICTURE.set()
#         await help_with_pic(message, state)


# @dp.callback_query_handler(lambda query: query.data.startswith('sup'), state=States.MANAGER_MODE)
# async def suppose_photo(query, state: FSMContext):
#     await bot.answer_callback_query(query.id)
#     async with state.proxy() as data:
#         data['cur_help_id'] = query.data.split(',')[1]
#     await shop(query.message)


# @dp.message_handler(state=States.HELP_WITH_PIC_NAME)
# async def handle_name(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['name'] = message.text
#         await message.reply(f'Ваше имя: {message.text}')
#     await help_with_pic(message, state)


# @dp.message_handler(state=States.HELP_ORD_NAME)
# async def handle_name(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['name'] = message.text
#         await message.reply(f'Ваше имя: {message.text}')
#     await help_with_pic(message, state)


@dp.message_handler(state='*')
async def change_state(message: types.Message, state: FSMContext):
    if message.text == favourites_button.text:
        await States.FAVOURITES.set()
        await favourites(message=message, state=state)
    elif message.text == shop_button.text:
        await States.CHOOSE_STYLE.set()
        await shop(message=message)
    # elif message.text == help_button.text:
    #     await States.HELP_WITH_PICTURE.set()
    #     await help_with_pic(message=message,state=state)
    else:
        await message.reply(unknown_command)



async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()
    session.close()


@dp.callback_query_handler(lambda query: query.data.split('#')[0] == 'character',state='*')
async def characters_page_callback(call,state: FSMContext):
    await bot.answer_callback_query(call.id)
    async with state.proxy() as data:
        page = int(call.data.split('#')[1])
        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id-1
        )
        await send_character_page(call.message, data,page)


async def send_character_page(message, data,page=1):
    user_id = int(message.chat.id)
    data['page'] = page
    paginator = InlineKeyboardPaginator(
        len(data['pictures_pagelist'])//2,
        current_page=page,
        data_pattern='character#{page}'
    )
    pic_ind=(page-1)*2
    cur_pics=data['pictures_pagelist'][pic_ind:pic_ind+2]
    for cur_pic in cur_pics:
        buy_pic = InlineKeyboardMarkup().\
            insert(InlineKeyboardButton('Купить 💎', callback_data='buy' + str(cur_pic.id))).\
            insert(InlineKeyboardButton('В избранное ♥', callback_data='fav' + str(cur_pic.id)))

        if cur_pic != cur_pics[-1] or len(data['pictures_pagelist'])<3:
            await bot.send_photo(user_id,
                                 cur_pic.ph_url,
                                 caption=f'{cur_pic.name}\n'
                                         f'Цена: {cur_pic.price} €\n'
                                         f'Автор: {cur_pic.author}\n'
                                         f'Размер: {cur_pic.size}\n'
                                         # f'Год написания: {cur_pic.year}\n'
                                         f'Материал/краски: {cur_pic.mats}\n'
                                         f'Стиль: {cur_pic.art_styles}',
                                 reply_markup=buy_pic)
        else:
            paginator.add_before(
                InlineKeyboardButton('Купить 💎', callback_data='buy' + str(cur_pic.id)),
                InlineKeyboardButton('В избранное ♥', callback_data='fav' + str(cur_pic.id))
            )
            await bot.send_photo(user_id,
                                 cur_pic.ph_url,
                                 caption=f'{cur_pic.name}\n'
                                         f'Цена: {cur_pic.price} €\n'
                                         f'Автор: {cur_pic.author}\n'
                                         f'Размер: {cur_pic.size}\n'
                                         # f'Год написания: {cur_pic.year}\n'
                                         f'Материал/краски: {cur_pic.mats}\n'
                                         f'Стиль: {cur_pic.art_styles}',
                                 reply_markup=paginator.markup)



#Base.metadata.create_all(engine1)
ssl_context = ssl.SSLContext()
engine = create_engine(f'postgresql+pg8000://{user}:{password}@{host}/{db_name}',
                       connect_args={'ssl_context': ssl_context},
                       #echo=True
                       )
#for tbl in reversed(Base.metadata.sorted_tables):
#    engine.execute(tbl.delete())

DBSession = sessionmaker(bind=engine)
session = DBSession()
#Base.metadata.create_all(engine)
#session.commit()
#bot['db'] = session
#executor.start_polling(dp,on_shutdown=session.close())


start_webhook(dispatcher=dp, webhook_path=WEBHOOK_PATH,
              on_startup=on_startup, on_shutdown=on_shutdown,
              host=WEBAPP_HOST, port=WEBAPP_PORT)




