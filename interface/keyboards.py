go_back_but = InlineKeyboardButton('Назад🔙', callback_data='go back')


give_choice_markup =InlineKeyboardMarkup() \
                    .insert(InlineKeyboardButton(_('Картой'), callback_data='card')) \
                    .insert(InlineKeyboardButton(_('Криптой'), callback_data='crypt')) \
                    .add(InlineKeyboardButton(_('Наличными (полная предоплата)'), callback_data='cash'))


crypt_choice = InlineKeyboardMarkup()\
    .insert(InlineKeyboardButton('BTC', callback_data='btc')) \
    .insert(InlineKeyboardButton('ETH', callback_data='eth')) \
    .add(InlineKeyboardButton('USDT', callback_data='usdt'))