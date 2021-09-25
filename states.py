from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    START_STATE = State()
    # HELP_WITH_PICTURE = State()
    HELP_WITH_PIC_NAME = State()
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
