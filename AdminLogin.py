from pyqiwip2p import QiwiP2P
import UserData
from DataBaseWork import DataBase
#[settings]#
settings = open("adminLogin.txt")
# 1194404057 testId

admin_id = str(settings.readline()).split('=')[1].replace(' ','')[:-1]
token = str(settings.readline()).split('=')[1].replace(' ','')[:-1]
print(admin_id)
#Token for QIWI
qiwi: QiwiP2P
QIWIToken = ""#"eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6InU2MjN5NC0wMCIsInVzZXJfaWQiOiI3OTIzNDk3ODA4MiIsInNlY3JldCI6ImUxNTI4YmQzY2Y1NmUxZTc5MzZiZDc3ODAyMDQyMDgzZWVmYTlkZjY5YjY0MDg2ZWUyZmZmODZlOTFhNjQ5MTcifX0="
#приветственное сообщение
HelloMessage = '''Вас приветствует...'''
#категории    {категория:{товары:[фото,описание,количество,размерный ряд, цена,количество в корзине,]}}
categories = {}
#люди и их id
ids = 1
people = {ids:[UserData.peopleProductsData(), {},[],[]]}
#count paid for statistic
countPAID = 0
#database
db = DataBase()
#кнопки
buttons = ["🌟 Главная", "💫 Товары", "🛒 Корзина", "❓Поддержка", "💌 Отзывы"]
buttonsAdmin  = ["⚙ Настройки","🗃️ Управление товарами", "📊 Статистика", "🔑 Платёжные системы"]
#уровни обработки текста(не трогать )


#текст на всех кнопках
#служба поддержки
supportSystem = '''Возникли проблемы? Вы можете связаться с нами'''
supportLink = str(settings.readline()).split('=')[1].replace(' ','')[:-1]
linkText = "Тут"

#отзывы
callSystem = '''Прочитать о нас вы можете '''
callLink = str(settings.readline()).split('=')[1].replace(' ','')[:-1]
linkTextCall = "Тут"
