from aiogram import Bot, types
from sqlalchemy.sql import text
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from sqlalchemy.future import select
import pandas as pd
from datetime import datetime
import os
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    START_STATE = State()
    HELP_WITH_PICTURE = State()
    BUY_PICTURE = State()
    CHOOSE_STYLE = State()
    CHOOSE_SHADES = State()
    LIST_OF_PICTURES = State()
    CUR_PICTURE = State()
    CUR_PICTURE_CONFIRMATION = State()
    ASK_FOR_CONTACT = State()
    MANAGER_MODE = State()
    FAVOURITES = State()

favourites_button = KeyboardButton('Избранное♥')
help_button = KeyboardButton('Подберите картину🖼️')
shop_button = KeyboardButton('Купить картину🏪')

global_markup = ReplyKeyboardMarkup(resize_keyboard=True).insert(
    favourites_button).insert(help_button).add(shop_button)


inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)


go_back_but = InlineKeyboardButton('Назад🔙',callback_data='go back')



markup_request = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('Отправить свой контакт ☎️', request_contact=True)
)


confirm_but=InlineKeyboardButton('Подтверждаю✔️', callback_data='confirmthis')

confirm_markup= InlineKeyboardMarkup().add(confirm_but)




start_message = 'Привет! Я - Искусство, как и ты, Человек. Только бот.' \
                'Здесь ты можешь выбрать картину на свой вкус или мои кореша-дизайнеры' \
                'помогут подобрать самую подходящую для твоего дома картину.'

select_style = 'Выберите стиль картин'
select_style_error = 'Такого стиля нет'


select_shade = 'Предпочтения в оттенках?'
select_shade_error = 'Такого оттенка не найдено'

manager_pending = 'Наш менеджер подтверждает заказ. В скором времени появится ' \
                  'ссылка для оплаты заказа'

successful_order = 'Спасибо за заказ!' \
                   'В скором времени с вами свяжется наш менеджер!'

help_pic_message = 'Ваши фото квартиры/жилого помещения (1-5 фото)'

help_message = 'Я - Искусство, как и ты, Человек. Только бот.' \
               'Здесь ты можешь выбрать картину на свой вкус или мои кореша-дизайнеры' \
               'помогут подобрать самую подходящую для твоего дома картину.' \
               'Для навигации используйте кнопки.'

unknown_command = 'Я вас не понимаю( Нажмите на кнопку.'


Base = declarative_base()


style_pic_table = Table('style_pic_table', Base.metadata,
                Column('style_id', Integer, ForeignKey('style.id')),
                Column('picture_id', Integer, ForeignKey('picture.id'))
)


shade_pic_table = Table('shade_pic_table', Base.metadata,
                Column('shade_id', Integer, ForeignKey('shade.id')),
                Column('picture_id', Integer, ForeignKey('picture.id'))
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
    __tablename__='picture'
    id = Column(Integer, primary_key=True)
    name = Column(String(63))
    ph_url = Column(String(255))
    size = Column(String(127))
    author = Column(String(127))
    price = Column(Integer)
    shades = relationship(
        'Shade',
        secondary=shade_pic_table,
        back_populates='pictures')
    styles = relationship(
        'Style',
        secondary=style_pic_table,
        back_populates='pictures')












TOKEN='1868938472:AAF3r1nERQeb4LK9IB5BiZ6VinLUZ9xXF-c'
public_key = 'sandbox_i63619417970'
private_key = 'sandbox_wW5EUlWQAGxjR1u0exfjeqbgRgxn4LOigEediUy7'
BUY_TOKEN='632593626:TEST:sandbox_i63619417970'
MY_ID = 344548620
DB_FILENAME = 'pictures.db'
secret_password = 'IAMART'
DB_URL = 'https://docs.google.com/spreadsheets/d/1a6In5Xc2eSA9PNt_ncHr6a8zbe8_33wIh8jOVje-NX4/gviz/tq?tqx=out:csv&sheet=Database'
MANAGER_IDS=['1586995361',
             ]

columns={'name':'Название картины',
         'styles':'Стиль/Стили',
         'shade':'Оттенок/Оттенки',
         'price':'Цена',
         'size':'Размер',
         'url':'URL фотографии',
         'author':'Автор'
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


# CATEGORY CHOOSE HANDLER
@dp.callback_query_handler(lambda query: query.data.startswith('cat'), state='*')
async def process_callback_styles(query, state : FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['category'] = query.data
    if 'cur_help_id' not in data:
        await States.CHOOSE_SHADES.set()
    db_session = bot.get("db")
    async with db_session() as session:
        shades = await session.execute(select(Shade))
        shades_inline = InlineKeyboardMarkup()
        for row in shades:
            item = row['Shade']
            shade = InlineKeyboardButton(item.name, callback_data='sha'+str(item.id))
            shades_inline.insert(shade)
    await bot.send_message(query['from'].id, "Выберите оттенок",reply_markup=shades_inline)


# SHADE CHOOSE HANDLER
@dp.callback_query_handler(lambda query: query.data.startswith('sha'),state='*')
async def process_callback_shades(query, state: FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        db_session = bot.get("db")
        async with db_session() as session:
            pictures_list = await session.execute(select(Picture)
                                             .filter(Picture.shades.any(id=int(query.data[3:])),
                                                     Picture.styles.any(id=int(data['category'][3:]))))
            await bot.send_message(query['from'].id, 'Вот ваши подобранные картины:')

            try:
                row = next(pictures_list)
                picture = row['Picture']
                buy_pic = InlineKeyboardMarkup() \
                    .insert(InlineKeyboardButton('Купить💎', callback_data='buy'+str(picture.id))) \
                    .insert(InlineKeyboardButton('В избранное♥', callback_data='fav' + str(picture.id)))
                await bot.send_photo(query['from'].id,
                                     picture.ph_url,
                                     caption=f'{picture.name}\n'
                                             f'Цена:{picture.price}\n'
                                             f'Автор:{picture.author}\n'
                                             f'Размер:{picture.size}',
                                     reply_markup=buy_pic)
                for row in pictures_list:
                    picture = row['Picture']
                    buy_pic = InlineKeyboardMarkup() \
                        .insert(InlineKeyboardButton('Купить💎', callback_data='buy'+str(picture.id))) \
                        .insert(InlineKeyboardButton('В избранное♥', callback_data='fav' + str(picture.id)))
                    await bot.send_photo(query['from'].id,
                                         picture.ph_url,
                                         caption=f'{picture.name}'
                                         f'Цена:{picture.price}\n'
                                         f'Автор:{picture.author}\n'
                                         f'Размер:{picture.size}',
                                         reply_markup=buy_pic)
            except StopIteration:
                pictures_list = await session.execute(select(Picture))
                for row in pictures_list:
                    picture = row['Picture']
                    buy_pic = InlineKeyboardMarkup() \
                        .insert(InlineKeyboardButton('Купить💎', callback_data='buy'+str(picture.id))) \
                        .insert(InlineKeyboardButton('В избранное♥', callback_data='fav' + str(picture.id)))
                    await bot.send_photo(query['from'].id,
                                         picture.ph_url,
                                         caption=f'{picture.name}'
                                         f'Цена:{picture.price}\n'
                                         f'Автор:{picture.author}\n'
                                         f'Размер:{picture.size}',
                                         reply_markup=buy_pic)
        if 'cur_help_id' not in data:
            await States.LIST_OF_PICTURES.set()


# SEND INVOICE
async def send_invoice(user_id,picture):
    user_id = int(user_id)
    state = dp.current_state(user=user_id, chat=user_id)
    async with state.proxy() as data:
        price = types.LabeledPrice(label=data['picture_name'], amount=data['price']*100)
        data["ord_cur_time"]=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        await bot.send_invoice(
            chat_id=user_id,
            title=data['picture_name'],
            description=f'Автор: {data["author"]}',
            provider_token=BUY_TOKEN,
            currency='uah',
            photo_url=data['photo_id'],
            photo_height=900,  # !=0/None or picture won't be shown
            photo_width=1200,
            is_flexible=False,  # True если конечная цена зависит от способа доставки
            prices=[price],
            start_parameter='time-machine-example',
            payload=f'{user_id} {data["ord_cur_time"]}',
            need_name=True,
            need_shipping_address=True,
        )


# CHECKOUT HANDLER
@dp.pre_checkout_query_handler(lambda query: True,state='*')
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# PAYMENT FEEDBACK
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT, state='*')
async def process_successful_payment(message: types.Message,state : FSMContext):
    await bot.send_message(message.chat.id, 'Оплата прошла успешно. Скоро мы с вами свяжемся!')
    order = message.successful_payment.order_info
    db_session = bot.get('db')
    async with state.proxy() as data:
        async with db_session() as session:
            await session.execute(text(f'DELETE FROM picture WHERE id = {data["pic_id"][3:]};'))
            await session.commit()
        for manager_id in MANAGER_IDS:
            await bot.send_message(manager_id,f'Прошла успешно оплата по картине {data["picture_name"]}\n'
                                              f'Цена: {data["price"]}\n'
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
async def manager_send_picture(user_id,pic_id,price,photo_id,picture_name,author,size):
    await bot.send_message(user_id,'Мы подобрали вам подходящую картину')
    await bot.send_photo(chat_id=user_id,photo=photo_id,caption=f'Вы подтверждаете картину {picture_name} ?'
                                                                f'Цена: {price}',reply_markup=confirm_markup)
    state = dp.current_state(chat=user_id,user=user_id)
    async with state.proxy() as data:
        data['pic_id'] = pic_id
        data['price'] = price
        data['photo_id'] = photo_id
        data['picture_name'] = picture_name
        data['author'] = author
        data['size'] = size


# PICTURE CONFIRMATION
@dp.callback_query_handler(lambda query:query.data.startswith('buy'),state='*')
async def process_callback_picture(query,state : FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['pic_id'] = query.data
        db_session = bot.get("db")
        async with db_session() as session:
            picture_list = await session.execute(select(Picture).filter(Picture.id==int(query.data[3:])))
            for picture_row in picture_list:
                picture = picture_row['Picture']
        if 'cur_help_id' in data:
            await manager_send_picture(data['cur_help_id'], picture.id, picture.price, picture.ph_url, picture.name)
        else:
            await bot.send_message(query['from'].id, f'Вы подтверждаете картину ?\n')
            data['price']=picture.price
            data['photo_id']=picture.ph_url
            data['picture_name']=picture.name
            data['size']=picture.size
            data['author']=picture.author
            await bot.send_photo(query['from'].id,
                                 picture.ph_url,
                                 caption=f'Ваша картина "{picture.name}"\n'
                                         f'Автор: {picture.author}\n'
                                         f'Размер: {picture.size}\n'
                                         f'Цена: {picture.price}\n',
                                 reply_markup=confirm_markup)
            await States.CUR_PICTURE_CONFIRMATION.set()


# DEL FROM FAVOURITES
@dp.callback_query_handler(lambda query:query.data.startswith('del'),state='*')
async def process_callback_rem_from_fav(query,state : FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['favourites'].remove(query.data[3:])
        await bot.send_message(query['from'].id, f'Картина {query.data[3:]} успешно удалена из любимых')


# ADD TO FAVOURITES
@dp.callback_query_handler(lambda query:query.data.startswith('fav'),state='*')
async def process_callback_add_to_fav(query,state : FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['favourites'].append(query.data[3:])
        await bot.send_message(query['from'].id, f'Картина {query.data[3:]} успешно добавлена в избранное')


# ASKING FOR CONTACT
@dp.callback_query_handler(lambda query: query.data == 'confirmthis',state='*')
async def process_callback_confirm(query,state : FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        if 'number' in data:
            await send_confirmation_to_manager(user_id=data['user_id'],
                                               picture_name = data['picture_name'],
                                               photo_id=data['photo_id'])
            answer =f'{manager_pending}'
            await bot.send_message(query['from'].id, answer)
        else:

            await bot.send_message(query['from'].id,"Нам нужен Ваш номер для связи" , reply_markup=markup_request)
            await States.ASK_FOR_CONTACT.set()


#CONTACT MANAGEMENT
@dp.message_handler(content_types=['contact'], state=States.ASK_FOR_CONTACT)
async def contact(message : types.Message,state : FSMContext):
    if message.contact is not None:
        await bot.send_message(message.chat.id, 'Вы успешно отправили свой номер',reply_markup=global_markup)
        async with state.proxy() as data:
            data['number'] = str(message.contact.phone_number)
            data['user_id'] = str(message.contact.user_id)
            answer = f'Ваш номер:{data["number"]}\n' \
                     f'\n{manager_pending}'
            await bot.send_message(message.chat.id, answer)
            await send_confirmation_to_manager(user_id=message.from_user.id,picture_name = data['picture_name'],photo_id=data['photo_id'])


async def send_confirmation_to_manager(user_id,picture_name,photo_id):
    for manager_id in MANAGER_IDS:
        confirm_manager_keyboard = InlineKeyboardMarkup().\
            insert(InlineKeyboardButton('Подтвердить',
                                        callback_data=f'm_conf,{user_id},{picture_name}')).\
            insert(InlineKeyboardButton('Нет в наличии',
                                        callback_data=f'm_disc,{user_id}'))
        await bot.send_message(manager_id,f'Заказ на картину {picture_name} {photo_id} от {user_id}',
                               reply_markup=confirm_manager_keyboard)


# manager confirm
@dp.callback_query_handler(lambda query: query.data.startswith('m_conf'),state='*')
async def managerconfirm(query):
    m_conf,user_id,picture = query.data.split(',')
    await bot.answer_callback_query(query.id)
    for manager_id in MANAGER_IDS:
        await bot.send_message(manager_id, f"Заказ на картину {picture} от {user_id} принят")
    await bot.send_message(user_id, "Ваш заказ подтвержден")
    await send_invoice(user_id, picture)

# manager confirm
@dp.callback_query_handler(lambda query: query.data.startswith('m_disc'),state='*')
async def managerconfirm(query):
    m_disc, user_id, picture = query.data.split(',')
    await bot.answer_callback_query(query.id)
    for manager_id in MANAGER_IDS:
        await bot.send_message(manager_id, f"Заказ на картину {picture} от {user_id} отклонен")
    await bot.send_message(user_id, "К сожалению, картины нет в наличии."
                                    " Вернитесь, пожалуйста в магазин и выберите другой вариант.")


# start message
@dp.message_handler(commands=['start'],state='*')
async def process_start_command(message: types.Message, state: FSMContext):
    await States.START_STATE.set()
    async with state.proxy() as data:
        if 'known_user' not in data:
            data['favourites'] = []
        data['known_user'] = '1'
    await message.reply(start_message,reply_markup=global_markup)


# help message
@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(help_message,reply_markup=global_markup)


# leave manager mode
@dp.message_handler(commands=['leave_manager'], state=States.MANAGER_MODE)
async def process_leave_manager(message: types.Message):
        await States.START_STATE.set()
        MANAGER_IDS.remove(message.from_user.id)
        await message.reply('Вы в стандартном режиме', reply_markup=global_markup)


# set manager mode
@dp.message_handler(commands=['go_manager'],state='*')
async def process_go_manager(message: types.Message):
    args = message.get_args()
    if args == secret_password:
        await States.MANAGER_MODE.set()
        MANAGER_IDS.append(message.from_user.id)
        await message.reply('Выставлен режим менеджера', reply_markup=global_markup)
    else:
        await message.reply('У вас нет доступа к этой комманде', reply_markup=global_markup)


#update database
@dp.message_handler(commands=['update_db'],state='*')
async def process_update_db(message: types.Message):
    args = message.get_args()
    if args == secret_password:
        db_session = bot.get('db')
        async with db_session() as session:
            await session.execute(text('DELETE FROM picture;'))
            await session.execute(text('DELETE FROM shade;'))
            await session.execute(text('DELETE FROM style;'))
            await session.execute(text('DELETE FROM shade_pic_table;'))
            await session.execute(text('DELETE FROM style_pic_table;'))
            await session.commit()
            df = pd.read_csv(DB_URL)
            for index, row in df.iterrows():
                shades = row[columns['shade']].replace(" ", "").split(',')
                styles = row[columns['styles']].replace(" ", "").split(',')
                picture = Picture(name=row[columns['name']],
                                  price=row[columns['price']],
                                  ph_url=row[columns['url']],
                                  size=row[columns['size']],
                                  author=row[columns['author']])
                for shade in shades:
                    try:
                        obj = next(await session.execute(select(Shade).filter(Shade.name == shade)))['Shade']
                        picture.shades.append(obj)
                    except:
                        picture.shades.append(Shade(name=shade))
                for style in styles:
                    try:
                        obj = next(await session.execute(select(Style).filter(Style.name == style)))['Style']
                        picture.styles.append(obj)
                    except:
                        picture.styles.append(Style(name=style))
                session.add(picture)
                await session.commit()
            await message.reply('База успешно обновлена', reply_markup=global_markup)
    else:
        await message.reply('У вас нет доступа к этой комманде', reply_markup=global_markup)


async def favourites(message: types.Message,state):
    async with state.proxy() as data:
        if len(data['favourites'])>0:
            await message.reply('Ваши любимые картины')
            await States.FAVOURITES.set()
            db_session = bot.get('db')
            async with db_session() as session:
                for picture_id in data['favourites']:
                    fav_pic = InlineKeyboardMarkup() \
                        .insert(InlineKeyboardButton('купить', callback_data='buy'+str(picture_id))) \
                        .insert(InlineKeyboardButton('удалить', callback_data='del' + picture_id))
                    picture = next(await session.execute(select(Picture).filter(Picture.id == int(picture_id))))['Picture']

                    await bot.send_photo(message.chat.id,
                                         picture.ph_url,
                                         caption=f'Ваша картина {picture.name}\n'
                                                 f'Цена : {picture.price}',
                                         reply_markup=fav_pic)
        else:
            await message.reply('У вас нет ничего :(. Перейдите в магазин, чтобы добавить картины в избранное:)')


async def shop(message: types.Message):
    db_session = bot.get("db")
    async with db_session() as session:
        styles = await session.execute(select(Style))
        styles_inline = InlineKeyboardMarkup()
        for row in styles:
            item = row['Style']
            style = InlineKeyboardButton(item.name, callback_data='cat'+str(item.id))
            styles_inline.insert(style)
    await message.reply('Выберите один из нескольких стилей для вашей картины',reply_markup=styles_inline)


async def help_with_pic(message: types.Message):
    await message.reply('Мы собрали все мировые силы, чтобы подобрать картину в ваш дом и сделать его еще уютнее. Отправьте нам несколько фото интерьера')


@dp.message_handler(content_types=['photo'],state=States.HELP_WITH_PICTURE)
async def handle_docs_photo(message : types.Message):
    await message.reply('Спасибо. Скоро мы отправим вам несколько вариантов.')
    suppose_keyboard=InlineKeyboardMarkup().insert(InlineKeyboardButton('подобрать',callback_data=f'sup,{message.from_user.id}'))
    for manager_id in MANAGER_IDS:
        await message.forward(manager_id)
        await bot.send_message(manager_id,f'Подобрать картину пользователю {message.from_user.username}',reply_markup=suppose_keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith('sup'),state=States.MANAGER_MODE)
async def suppose_photo(query,state : FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        data['cur_help_id']=query.data.split(',')[1]
    await shop(query.message)


@dp.message_handler(state='*')
async def change_state(message: types.Message,state : FSMContext):
    if message.text == favourites_button.text:
        await States.FAVOURITES.set()
        await favourites(message=message,state=state)
    elif message.text == shop_button.text:
        await States.CHOOSE_STYLE.set()
        await shop(message=message)
    elif message.text == help_button.text:
        await States.HELP_WITH_PICTURE.set()
        await help_with_pic(message=message)
    else:
        await message.reply(unknown_command)


async def main():
    engine = create_async_engine(f'sqlite+aiosqlite:///{DB_FILENAME}')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    bot['db']=async_session
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


asyncio.run(main())