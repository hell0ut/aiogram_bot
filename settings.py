import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread

MAX_SUM_ALLOWED_PER_OP = 4500
TOKEN = os.environ['BOT_TOKEN']
public_key = os.environ['PUBLIC_KEY']
private_key = os.environ['PRIVATE_KEY']
BUY_TOKEN = os.environ['BUY_TOKEN']
MY_ID = 344548620 #for debugging purposes
MANAGER_IDS = set(os.environ['MANAGER_IDS'].split(','))
DB_FILENAME = 'pictures.db' #sqlite test
secret_password = 'IAMART' #manager command password
DB_URL = os.environ['GOOGLE_SHEETS_DB']


BTC_T=os.environ['BTC_TOKEN']
ETH_T=os.environ['ETH_TOKEN']
USDT_T=os.environ['USDT_TOKEN']


host=os.environ['AWS_URL']
db_name='postgres'
user='postgres'
password=os.environ['POSTGRES_PASSWORD']


WEBHOOK_HOST = os.environ['WEBHOOK_HOST']  # name your app
WEBHOOK_PATH = '/webhook/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.environ.get('PORT')


scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
db_sheet = client.open_by_key(GOOGLE_API_KEY).sheet1
sold_sheet = client.open_by_key(GOOGLE_API_KEY).worksheets()[2]

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