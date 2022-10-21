# -*- coding: utf-8 -*-


# out settings
from multiprocessing.dummy import Pool
from pyqiwip2p import QiwiP2P

import AdminLogin
import UserData
from AdminLogin import token, admin_id, categories, \
    buttons, buttonsAdmin
from aiogram.utils import executor

from aiogram.utils.markdown import hlink

from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher


from random import randint

bot = Bot(token=token)
dp = Dispatcher(bot)
storage = MemoryStorage()
# dynamic value
index = 0



class stateSec():
    isChangedList = {"pro_name": [0, ""],
                     "photo_name": [0, ""],
                     "description_name": [0, ""],
                     "price_name": [0, ""]}
    idCollect = ""


pool = Pool(20)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.from_user.id not in AdminLogin.people.keys():
        #0 - userData obj 1 - basket 2- nameproducts 3 - product
        AdminLogin.people.update({message.from_user.id:[UserData.peopleProductsData(), {},[],[]]})
        AdminLogin.ids = message.from_user.id


    # добавление новых кнопок для пользователя

    keyboard.add(*buttons)
    # новые кнопки для админа

    if admin_id == str(message.from_user.id):
        keyboard.add(*buttonsAdmin)

    await message.answer("Если у вас отсутствует меню,\nто попробуйте ввести /start ", reply_markup=keyboard)


@dp.message_handler(text=["Вернуться на главную"])
@dp.callback_query_handler(text=['Вернуться на главную'])
async def categoriesFunction(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.from_user.id not in AdminLogin.people.keys():
        #0 - userData obj 1 - basket 2- nameproducts 3 - product
        AdminLogin.people.update({message.from_user.id:[UserData.peopleProductsData(), {},[],[]]})
        AdminLogin.ids = message.from_user.id
    # добавление новых кнопок для пользователя
    await message.answer("Если у вас отсутствует меню,\nто попробуйте ввести /start ", reply_markup=keyboard)
    keyboard.add(*buttons)
    # новые кнопки для админа
    if admin_id == str(message.from_user.id):
        keyboard.add(*buttonsAdmin)
    await message.answer("Выберите один из элементов меню", reply_markup=keyboard)

#проблема принять id
@dp.callback_query_handler(text_contains= "--userid--")
async def deleteFromBasket(call: types.CallbackQuery):

    sDate = call.data[:-10]

    try:

        AdminLogin.people[call.from_user.id][0].backetSum -= \
            AdminLogin.people[call.from_user.id][1][int(sDate)][1] * \
            AdminLogin.people[call.from_user.id][1][int(sDate)][2]
        AdminLogin.people[call.from_user.id][1].pop(int(sDate))
        await call.message.answer(f"Товар под номером {sDate} удален из корзины")
    except Exception:
        await call.message.answer("В корзине нет такого элемента")


# delete from basket
@dp.message_handler(text=["Удалить элемент", "Очистить корзину полностью"])
async def deleteButtonsBasket(message: types.Message):
    if message.text == "Очистить корзину полностью":

        print(message.from_user.id)
        AdminLogin.people[message.from_user.id][1].clear()
        await message.answer("Корзина очищена")
    else:

        keyboard = types.InlineKeyboardMarkup()
        # добавление новых кнопок товаров из корзины для удаления
        if AdminLogin.people[message.from_user.id][1].keys():

            for i in AdminLogin.people[message.from_user.id][1].keys():
                keyboard.add(types.InlineKeyboardButton(text=f"{i}", callback_data=str(i)+"--userid--"))

            await message.answer("Выберите номер элемента который желаете удалить из корзины", reply_markup=keyboard)
        else:
            await message.answer("Корзина пуста")


# paying
@dp.message_handler(text=["✅ Оплатить"])
async def Paying(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(types.InlineKeyboardButton(text="QIWI", callback_data="QIWI"))

    await message.answer("Выберите способ оплаты", reply_markup=keyboard)


# QIWI and Another type
@dp.callback_query_handler(text=["QIWI"])
async def QIWIbuttons(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    keyboard = types.InlineKeyboardMarkup()
    if call.data == "QIWI":
        if AdminLogin.people[call.from_user.id][1]:

            try:

                bill = AdminLogin.qiwi.bill(amount=AdminLogin.people[call.from_user.id][0].backetSum, lifetime=30,
                                            comment=str(call.message.from_user.id) + "_" + str(randint(1000, 9999)))



                keyboard.add(types.InlineKeyboardButton(text="Оплатить", url=bill.pay_url))
                keyboard.add(
                    types.InlineKeyboardButton(text="Проверить оплату", callback_data="check_" + str(bill.bill_id)))

                await call.message.answer(f"Оплата счета на сумму {AdminLogin.people[call.from_user.id][0].backetSum} руб "
                                        f"\nПосле оплаты оязательно нажмите проверить оплату, иначе оплата не пройдет!!!", reply_markup=keyboard)

            except Exception as e:
                await call.message.answer("Админ не добавил свой счет для оплаты")
        else:
            await call.message.answer("Добавьте товар в корзину перед покупкой")
    else:
        await call.message.answer("Данная функция еще не доступна")


# callback messges check
@dp.callback_query_handler(text_contains="check_")
async def Check(call: types.CallbackQuery):
    bill = str(call.data[6:])
    if not AdminLogin.db.isWasPaid(bill):
        if bill:
            if str(AdminLogin.qiwi.check(bill_id=bill).status) == "PAID":
                # middleOfPrise.append(UserData.backetSum)
                product = [i for i in AdminLogin.people[call.from_user.id][1].keys()]
                countProduct = [i[3] for i in AdminLogin.people[call.from_user.id][3]]
                #add user to database
                AdminLogin.db.addNewPAID(int(call.from_user.id),
                                         str(call.from_user.username),
                                         str(bill),
                                         str(product)
                                         ,str(countProduct))

                AdminLogin.people[call.from_user.id][0].backetSum = 0
                AdminLogin.people[call.from_user.id][1].clear()
                AdminLogin.people[call.from_user.id][2].clear()
                AdminLogin.people[call.from_user.id][3].clear()
                AdminLogin.countPAID += 1
                bill = ""
                await call.message.answer(
                    f"Спасибо за покупку\n ваш чек на оплату {bill}.\nВскоре с вами свяжутся администраторы")

            else:
                await call.message.answer(
                    "Вы не оплатили счет, если что-то пошло не так:\n напишите в службу поддержки или повторите операцию")
        else:
            await call.message.answer("Счет не найден")
    else:
        await call.message.answer("Ваш счет был оплачен")


# main handler for user
@dp.message_handler(text=buttons)
async def categoriesFunction(message: types.Message):
    # main
    if message.text == buttons[0]:
        await message.answer(AdminLogin.HelloMessage)
    # categories
    if message.text == buttons[1]:
        keyboard = types.InlineKeyboardMarkup()

        for i in categories.keys():
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i))

        if categories.keys():
            await message.answer("Выберите категорию товара", reply_markup=keyboard)
        else:
            await message.answer("Товаров пока нет в наличии", reply_markup=keyboard)
    # backet
    if message.text == buttons[2]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        if AdminLogin.people[message.from_user.id][1].keys():
            backetMessage = ""

            for i, j in AdminLogin.people[message.from_user.id][1].items():
                backetMessage += f"Название: {j[0]}\n Цена за {j[2]}: {int(j[1]) * j[2]} руб\n"
                backetMessage += f"Номер товара: {i}\n\n\n"

            backetMessage += "Общая сумма: " + str(AdminLogin.people[message.from_user.id][0].backetSum) + " руб"
            keyboard.add(*["Удалить элемент"])
            keyboard.add(*["Очистить корзину полностью"])

            keyboard.add(*["✅ Оплатить"])
            keyboard.add(*["Вернуться на главную"])

            await message.answer(text=backetMessage, reply_markup=keyboard)
        else:

            keyboard.add("Вернуться на главную")
            await message.answer("Корзина все еще пуста", reply_markup=keyboard)

    if message.text == buttons[3]:
        await message.answer(text=AdminLogin.supportSystem + " " + hlink(AdminLogin.linkText, AdminLogin.supportLink),
                             parse_mode="HTML")

    if message.text == buttons[4]:
        await message.answer(text=AdminLogin.callSystem + " " + hlink(AdminLogin.linkTextCall, AdminLogin.callLink),
                             parse_mode="HTML")


# main handler for admin
@dp.message_handler(text=buttonsAdmin)
async def AdminButtonHandler(message: types.Message):
    # main

    if message.text == buttonsAdmin[0]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["Изменить текст главного окна", "Изменить категории"])

        keyboard.add("Вернуться на главную")
        await message.answer("<---Изменения--->", reply_markup=keyboard)
    # add p
    if message.text == buttonsAdmin[1]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["Добавить новый товар в категорию", "Удалить товар из категории"])

        keyboard.add("Вернуться на главную")
        await message.answer("<---Изменения--->", reply_markup=keyboard)




    # statistic
    if message.text == buttonsAdmin[2]:


        await message.answer(f"Статистика\n\nКоличество пользователей : {len(AdminLogin.people.keys())-1}"
                             f"\n\nКоличество покупок : {AdminLogin.countPAID}")

    #Pay
    if message.text == buttonsAdmin[3]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["Изменить счет QIWI", "Добавить счет QIWI"])
        keyboard.add("Вернуться на главную")
        await message.answer("Выберите один из пунктов меню", reply_markup=keyboard)

@dp.message_handler(text=["Добавить новый товар в категорию", "Удалить товар из категории"])
async def categoriesFunction(message: types.Message):
    if message.text == "Удалить товар из категории":
        keyboard = types.InlineKeyboardMarkup()

        for i in categories.keys():
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i + "--deleteid--"))

        if categories.keys():
            await message.answer("Выберите категорию в которой требуется удалить товар", reply_markup=keyboard)
        else:
            await message.answer("Категорий товаров пока нет", reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()

        for i in categories.keys():
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i + "--changesid--"))

        if categories.keys():
            await message.answer("Выберите категорию в которую требуется добавить товар", reply_markup=keyboard)
        else:
            await message.answer("Категорий товаров пока нет", reply_markup=keyboard)
@dp.callback_query_handler(text_contains="--deleteid--")
async def ProductAddedFunction(call: types.CallbackQuery):
    idCollect = call.data[:-12]
    stateSec.idCollect = idCollect
    keyboard = types.InlineKeyboardMarkup()

    for i,j in categories[idCollect].items():
        keyboard.add(types.InlineKeyboardButton(text=j[-1], callback_data=i + "--deletePid--"))

    if categories[idCollect].keys():
        await call.message.answer("Выберите номер товара", reply_markup=keyboard)
    else:
        await call.message.answer("В данной категории пока нет товаров", reply_markup=keyboard)

@dp.callback_query_handler(text_contains="--deletePid--")
async def ProductAddedFunction(call: types.CallbackQuery):
    idProduct = call.data[:-13]


    try:
        categories[stateSec.idCollect].pop(idProduct)
        await call.message.answer("Товар был удален")
    except:
        await call.message.answer("В данной категории такого товара нет")

# Добавление нового товара
@dp.callback_query_handler(text_contains="--changesid--")
async def ProductAddedFunction(call: types.CallbackQuery):
    idCollect = call.data[:-13]

    stateSec.idCollect = idCollect
    # callers to
    await call.message.answer("Введите название товара")
    stateSec.isChangedList["pro_name"][0] = 1
@dp.message_handler(text=["Изменить текст главного окна", "Изменить категории"])
async def ChangeCheck(message: types.Message):

    if message.text == "Изменить текст главного окна":
        await message.answer("Введите текст который вы хотите вставить в вывод кнопки ГЛАВНАЯ")
        AdminLogin.people[message.from_user.id][1].isChangedList["main"] = 1
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*["Удалить категорию", "Добавить категорию", "Изменить название"])
        keyboard.add("Вернуться на главную")
        await message.answer("Выберите операцию над областью категорий", reply_markup=keyboard)

def adderToCollection():
    randomsId = randint(0, 9999999)
    while randomsId in categories[stateSec.idCollect].values():
        randomsId = randint(0, 999999)
    AdminLogin.categories[stateSec.idCollect].update({stateSec.isChangedList["pro_name"][1]:
                                 [stateSec.isChangedList["photo_name"][1],
                                  stateSec.isChangedList["description_name"][1],
                                  stateSec.isChangedList["price_name"][1]
                                     , 0
                                     , randomsId]})



@dp.message_handler(content_types=["photo"])
async def PhotoProduct(message: types.Message):
    global index
    if stateSec.isChangedList["photo_name"][0] == 1:
        try:
            await message.photo[-1].download(destination_file=f'photos\photo{index}.jpg')
            stateSec.isChangedList["photo_name"][1] = f'photos\photo{index}.jpg'
            print(stateSec.isChangedList["photo_name"][1])
            index+=1
            stateSec.isChangedList["photo_name"][0] = 0
            await message.answer("Фотография успешно загружена")
            await message.answer("Введите описание товара")
            stateSec.isChangedList["description_name"][0] = 1
        except:
            await message.answer("Фотография не была загружена попробуйте снова")


@dp.message_handler(text=["Удалить категорию", "Добавить категорию", "Изменить название"])
async def ChangeCheck(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    if message.text == "Удалить категорию":

        for i in categories.keys():
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i + "--deleted--"))
        await message.answer("Выберите категорию для удаления", reply_markup=keyboard)
    elif message.text == "Добавить категорию":
        AdminLogin.people[message.from_user.id][0].isChangedList["add"] = 1
        AdminLogin.people[message.from_user.id][0].isChangedList["ch-e"] = 0
        await message.answer("Введите название новой категории")
    else:
        AdminLogin.people[message.from_user.id][0].isChangedList["add"] = 0
        for i in categories.keys():
            keyboard.add(types.InlineKeyboardButton(text=i, callback_data=i + "--changed--"))

        await message.answer("Выберите категорию для изменения названия", reply_markup=keyboard)


@dp.callback_query_handler(text_contains="--deleted--")
async def ProductFunction(call: types.CallbackQuery):
    categories.pop(call.data[:-11])
    await call.message.answer("Категория успешно удалена")


@dp.callback_query_handler(text_contains="--changed--")
async def ProductFunction(call: types.CallbackQuery):
    AdminLogin.people[call.from_user.id][0].oldKey = call.data[:-11]
    AdminLogin.people[call.from_user.id][0].isChangedList["ch-e"] = 1
    await call.message.answer("Введите новое название для категории")


@dp.message_handler(text=["Изменить счет QIWI", "Добавить счет QIWI"])
async def ChangeCheck(message: types.Message):
    if message.text == "Изменить счет QIWI":
        try:
            if AdminLogin.qiwi:
                AdminLogin.people[message.from_user.id][0].isChange = 1
                await message.answer("Введите новый токен счета")
        except Exception:
            await message.answer("У вас еще нету счета нужно добавить счет")
    else:
        AdminLogin.people[message.from_user.id][0].isChange = 1

        await message.answer("Напишите сюда тайный токен вашего QIWI кошелька \n"
                             "это можно сделать " + hlink("ТУТ", "https://qiwi.com/p2p-admin/api"), parse_mode="HTML")


# after categories handler categories
@dp.callback_query_handler(text=categories.keys())
async def ProductFunction(call: types.CallbackQuery):
    if not categories[call.data]:
        await call.message.answer("В данной категории еще нет товаров")
        return

    AdminLogin.people[call.from_user.id][2].clear()
    AdminLogin.people[call.from_user.id][3].clear()
    AdminLogin.people[call.from_user.id][0].currentProduct = 0
    for i, j in categories[call.data].items():
        AdminLogin.people[call.from_user.id][2].append(i)
        AdminLogin.people[call.from_user.id][3].append(j)

        # изображение текущего экземпляра

    photo = ""

    try:
        photo = open(AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][0], "rb")
    except Exception:
        pass



    if photo != "":
        keyboard = types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton(text="⬅ Предыдущий", callback_data="Back"),

            types.InlineKeyboardButton(text="Следующий ➡", callback_data="Next")
        ).row().add(types.InlineKeyboardButton(text="В корзину", callback_data="В корзину"))
        await bot.send_photo(photo=photo,
                             chat_id=call.message.chat.id,
                             caption=f"Название: {AdminLogin.people[call.from_user.id][2][AdminLogin.people[call.from_user.id][0].currentProduct]}\n\n" \
                                     f"Описание: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][1]}\n\n" \
 \
                                     f"Цена: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][2]} руб\n\n"
                                    f"Номер товара: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][-1]}",
                             reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton(text="Предыдущий", callback_data="Back"),

            types.InlineKeyboardButton(text="Следующий", callback_data="Next")
        ).row().add(types.InlineKeyboardButton(text="В корзину", callback_data="В корзину"))
        await call.message.answer(f"Название: {AdminLogin.people[call.from_user.id][2][AdminLogin.people[call.from_user.id][0].currentProduct]}\n\n"
                                  f"Описание: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][1]}\n\n"
                                  f"Цена: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][2]} руб\n\n"
                                  f"Номер товара: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][-1]}", reply_markup=keyboard)


@dp.callback_query_handler(text=["Next", "Back"])
async def ProductSplitFunction(call: types.CallbackQuery):
    if call.data == "Next":
        AdminLogin.people[call.from_user.id][0].currentProduct += 1
    if call.data == "Back":
        AdminLogin.people[call.from_user.id][0].currentProduct -= 1
    if 0 > AdminLogin.people[call.from_user.id][0].currentProduct:
        AdminLogin.people[call.from_user.id][0].currentProduct = len(AdminLogin.people[call.from_user.id][3]) - 1
    if len(AdminLogin.people[call.from_user.id][3]) <= AdminLogin.people[call.from_user.id][0].currentProduct:
        AdminLogin.people[call.from_user.id][0].currentProduct = 0
    photo = ""
    try:
        photo = open(AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][0], "rb")
    except:
        pass
    if photo != "":
        keyboard = types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton(text="⬅ Предыдущий", callback_data="Back"),

            types.InlineKeyboardButton(text="Следующий ➡", callback_data="Next")
        ).row().add(types.InlineKeyboardButton(text="В корзину", callback_data="В корзину"))
        await bot.send_photo(photo=photo,
                             chat_id=call.message.chat.id,
                             caption=f"Название: {AdminLogin.people[call.from_user.id][2][AdminLogin.people[call.from_user.id][0].currentProduct]}\n\n" \
                                     f"Описание: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][1]}\n\n" \
 \
                                     f"Цена: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][2]} руб\n\n"
                             f"Номер товара: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][-1]}",
                             reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton(text="Предыдущий", callback_data="Back"),

            types.InlineKeyboardButton(text="Следующий", callback_data="Next")
        ).row().add(types.InlineKeyboardButton(text="В корзину", callback_data="В корзину"))
        await call.message.answer(f"Название: {AdminLogin.people[call.from_user.id][2][AdminLogin.people[call.from_user.id][0].currentProduct]}\n\n"
                                  f"Описание: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][1]}\n\n"
                                  f"Цена: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][2]} руб\n\n"
                                  f"Номер товара: {AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][-1]}", reply_markup=keyboard)


@dp.callback_query_handler(text=["В корзину"])
async def BasketFunction(call: types.CallbackQuery):
    try:
        AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][3] += 1
        AdminLogin.people[call.from_user.id][1][AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][-1]] = \
            [AdminLogin.people[call.from_user.id][2][AdminLogin.people[call.from_user.id][0].currentProduct],
             AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][2],
             AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][3]]

        AdminLogin.people[call.from_user.id][0].backetSum += int(AdminLogin.people[call.from_user.id][3][AdminLogin.people[call.from_user.id][0].currentProduct][2])
        await call.message.answer("Успешно добавлено в корзину")
    except Exception:
        await call.message.answer("Что-то пошло не так")
# all operation with just a text
@dp.message_handler(content_types=["text"])
async def textProcessing(message: types.Message):
    if AdminLogin.people[message.from_user.id][0].isChange == 1:
        try:
            AdminLogin.qiwi = QiwiP2P(auth_key=message.text)
            AdminLogin.QIWIToken = message.text
            AdminLogin.people[message.from_user.id][0].isChange = 0
            await message.answer("Вы были авторизованы!!! Теперь вы можете получать оплату с сервиса")
        except:
            await message.answer("Неверный токен попробуйте заново")

    elif AdminLogin.people[message.from_user.id][0].isChangedList["add"] == 1:
        if message.text not in categories.keys():
            categories[message.text] = {}
            AdminLogin.people[message.from_user.id][0].isChangedList["add"] = 0
            await message.answer("Категория успешно добавлена")
        else:
            await message.answer("Такая категория уже существует придумайте новое название")
    elif AdminLogin.people[message.from_user.id][0].isChangedList["ch-e"] == 1:
        categories[message.text] = categories.pop(AdminLogin.people[message.from_user.id][0].oldKey)
        AdminLogin.people[message.from_user.id][0].isChangedList["ch-e"] = 0
        await message.answer("Категория успешно изменена")
    elif AdminLogin.people[message.from_user.id][0].isChangedList["main"] == 1:
        AdminLogin.HelloMessage = message.text
        await message.answer("Текст успешно изменен")
        AdminLogin.people[message.from_user.id][0].isChangedList["main"] = 0
    elif stateSec.isChangedList["pro_name"][0] == 1:
        # call next element from stateSec
        stateSec.isChangedList["pro_name"][1] = message.text
        stateSec.isChangedList["photo_name"][0] = 1
        stateSec.isChangedList['description_name'][0] = 1
        stateSec.isChangedList["pro_name"][0] = 0

        await message.answer("Название добавлено")
        await message.answer("Отправьте картинку товара или сразу перейдите к описанию")
    elif stateSec.isChangedList["description_name"][0] == 1:
        stateSec.isChangedList["description_name"][1] = message.text
        stateSec.isChangedList["description_name"][0] = 0
        stateSec.isChangedList["photo_name"][0] = 0
        stateSec.isChangedList["price_name"][0] = 1

        await message.answer("Описание добавлено")
        await message.answer("Введите цену товара (обязательно число)")


    elif stateSec.isChangedList["price_name"][0] == 1:
        try:
            stateSec.isChangedList["price_name"][1] = int(message.text)

            stateSec.isChangedList["price_name"][0] = 0
            adderToCollection()
            await message.answer("Готово!!!проверьте ТОВАРЫ")

        except:
            await message.answer("В введённых данных присутствовали не только цифры попробуйте снова")


executor.start_polling(dp, skip_updates=True)
