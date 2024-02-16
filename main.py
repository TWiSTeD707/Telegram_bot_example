import telebot
from main2 import keyboard, back_menu
from message import hello
from message import date
import random

bot = telebot.TeleBot('')
chat_id = ''


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.forward_message(chat_id, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, hello, reply_markup=keyboard)


@bot.message_handler(commands=['cost'])
def process_weight_step(message):
    bot.forward_message(chat_id, message.chat.id, message.message_id)
    bot.send_message(message.chat.id,
                     'Сейчас я расчитаю стоимость вашего заказа.\n\nВведите стоимость товаров в юанях или отправьте '
                     'слово "отмена", чтобы отменить расчёт: ')
    bot.register_next_step_handler(message, process_cost_step)


def process_cost_step(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Расчет отменен.\n Можете нажать команду /start чтобы продолжить работу.')
        return
    try:
        cost = float(message.text)
        bot.forward_message(chat_id, message.chat.id, message.message_id)
    except ValueError:
        bot.send_message(message.chat.id,
                         'Вы ввели некорректную стоимость, попробуйте еще раз или отправьте слово "отмена", '
                         'чтобы отменить расчёт.')
        bot.register_next_step_handler(message, process_cost_step)
    else:
        bot.send_message(message.chat.id, 'Спасибо! Теперь введите вес вашего заказа в килограммах (например 1.5)')
        bot.register_next_step_handler(message, process_delivery_step, cost)


def process_delivery_step(message, cost):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Расчет отменен.\n Можете нажать команду /start чтобы продолжить работу.')
        return
    try:
        weight = float(message.text.strip())
        bot.forward_message(chat_id, message.chat.id, message.message_id)
    except ValueError:
        bot.send_message(message.chat.id, 'Ошибка! Введите числовое значение для веса товаров в килограммах - 1.5')
        bot.register_next_step_handler(message, process_delivery_step, cost)
    else:
        bot.send_message(message.chat.id, 'Введите стоимость доставки в рублях: (549/649/849)\nКатегории доставки:\n'
                                          'Эконом - 549 рублей (за 1 кг) - доставка ~ 30 - 45 дней\n'
                                          'Стандарт - 649 рублей (за 1 кг) - доставка ~ 18 - 28 дней\n'
                                          'Ультра - 849 рублей (за 1 кг) - доставка ~ 15 - 20 дней')
        bot.register_next_step_handler(message, get_delivery_cost, cost, weight)


def get_delivery_cost(message, cost, weight):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Расчет отменен.\n Можете нажать команду /start чтобы продолжить работу.')
        return
    if message.text.strip() in ('549', '649', '849'):
        delivery_cost = int(message.text.strip())
        bot.forward_message(chat_id, message.chat.id, message.message_id)
        total_cost1 = (cost * date()) * 1.15 + delivery_cost * weight
        bot.send_message(message.chat.id, 'стоимость вашего заказа составляет: {:.2f} рублей'.format(total_cost1))
    else:
        bot.send_message(message.chat.id, 'Ошибка! Введите стоимость доставки из списка: 549, 649, 849')
        bot.register_next_step_handler(message, get_delivery_cost, cost, weight)


def cancel_order(message):
    bot.send_message(message.chat.id, f"Окей,{message.from_user.first_name} ваш заказ отменен. Нажмите /start, "
                                      f"чтобы начать заново.")


@bot.message_handler(commands=['order'])
def handle_order_command(message):
    bot.forward_message(chat_id, message.chat.id, message.message_id)
    user = message.from_user.first_name
    bot.forward_message(chat_id, message.chat.id, message.message_id)

    instructions = 'Чтобы оформить заказ, отправьте следующие данные в формате:\n\n' \
                   'Ссылки товаров\n' \
                   'Вариант доставки\n\n' \
                   'Например, так:\n' \
                   'https://www.example.com/item1.png, https://www.example.com/item2.png\n' \
                   'Эконом\n\n' \
                   'Наши варианты доставки:\n' \
                   'Эконом: 549 рублей (за 1 кг) - доставка ~ 30 - 45 дней\n\n' \
                   'Стандарт: 649 рублей (за 1 кг) - доставка ~ 18 - 28 дней\n\n' \
                   'Ультра: 849 рублей (за 1 кг) - доставка ~ 15 - 20 дней\n\n' \
                   'Чтобы отменить заказ напишите боту: отменить заказ'

    bot.send_message(message.chat.id, f'Привет, {user}! {instructions}')
    bot.register_next_step_handler(message, order_handler, user)


def order_handler(message, user):
    if message.text.lower() == "отменить заказ":
        cancel_order(message)
        return
    user = f'@{message.from_user.username}'
    lines = message.text.strip().split('\n')
    if len(lines) != 2:
        bot.send_message(message.chat.id, 'Ой! Необходимо ввести 2 строки данных по образцу:\n'
                                          'Ссылки на товары (одна или несколько, через запятую)\n'
                                          'Способ доставки (Эконом, Стандарт, Ультра)')
        bot.register_next_step_handler(message, order_handler, user)
    else:
        items = lines[0]
        if not items or not any(x.startswith('http') for x in items.split('\n')):
            bot.send_message(message.chat.id, 'Пожалуйста, введите ссылки на товары (Через запятую) :')
            bot.register_next_step_handler(message, order_handler, user)
            return
        delivery_method = lines[1].lower()
        if delivery_method not in ('эконом', 'стандарт', 'ультра'):
            bot.send_message(message.chat.id,
                             'Пожалуйста, выберите один из вариантов доставки:\n Эконом, Стандарт или Ультра:\n'
                             'Эконом - 549 рублей (за 1 кг) - доставка ~ 30 - 45 дней\n'
                             'Стандарт - 649 рублей (за 1 кг) - доставка ~ 18 - 28 дней\n'
                             'Ультра - 849 рублей (за 1 кг) - доставка ~ 15 - 20 дней')

            bot.register_next_step_handler(message, order_handler, user)
            return
        staff_members = ['@orloxxx', '@benzo_korshun', '@DDMITRIEVICH04']
        staff_member = random.choice(staff_members)

        order_msg = f'Новый заказ:\n' \
                    f'Имя: {user}\n' \
                    f'Товары: {items}\n' \
                    f'Способ доставки: {delivery_method}\n' \
                    f'Ответственный: {staff_member}'

        bot.send_message(-957120772, order_msg)
        bot.send_message(message.chat.id, f'{user}, ваш заказ принят! Ожидайте ответа оператора.')


@bot.message_handler(content_types=['location'])
def handle_location(message):
    bot.reply_to(message, "Ну и зачем оно мне?")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "Вау, видео! Можно подумать я его когда то посмотрю.")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.reply_to(message, "Какой красивый у тебя голос! 110010110111, а ой. Ты же не слышишь это...")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    bot.reply_to(message, "Отправь мне все свои файлы, я всё равно их не читаю.")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    bot.reply_to(message, "Как-нибудь послушаю этот трек.")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    bot.reply_to(message, "Хватит хвастаться своими стикерами! У меня их нет!")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    bot.reply_to(message, "Красивая фотокарточка наверное. Жаль я не умею смотреть на картинки :(")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.reply_to(message, "К чему это? Я не понимаю. Попробуйте написать из того, что я прочитаю.")
    bot.forward_message(chat_id, message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call: telebot.types.CallbackQuery):
    if call.data == 'option1':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Наши контакты для связи:\n@ - менеджер по продажам и '
                                   'финансам\n@ -'
                                   'менеджер по продажам и рекламе\n@ - менеджер по продажам, '
                                   'логист\n@ - IT-менеджер, программист',
                              reply_markup=back_menu)
    elif call.data == 'option2':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Наша компания предоставляет три класса услуг по доставке товара из '
                                   'Китая в Россию:\n\nДоставка \"Эконом\":\n549 рублей (за 1 кг) - '
                                   'доставка ~ 30 - 45 дней\n\nДоставка \"Стандарт\":\n649 рублей (за 1 кг) '
                                   '- доставка ~ 18 - 28 дней\n\nДоставка \"Ультра\":\n849 рублей (за 1 кг) '
                                   '- доставка ~ 15 - 20 дней\n\nПо поводу доставки до вашего города (если '
                                   'вы не из Ижевска) - писать в личные сообщения продавцам.',
                              reply_markup=back_menu)
    elif call.data == 'option3':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Это пример площадок, с которых вы можете заказать товары через нашу компанию\n'
                                   '(По остальным компаниям писать - @DDMITRIEVICH04)\n\n'
                                   '1.Taobao - https://www.taobao.com/\n'
                                   '2. 1688 - https://www.1688.com/\n'
                                   '3. Poizon - https://www.poizon.com/\n',
                              reply_markup=back_menu)
    elif call.data == 'option4':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Сделаем самый надежный легит чек любого товара!\nСтоимость: 300 рублей\nПо поводу '
                                   'этой услуги обращайтесь к @benzo_korshun',
                              reply_markup=back_menu)
    elif call.data == 'option5':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='https://vk.com/redlinelogistics',
                              reply_markup=back_menu)
    elif call.data == 'option6':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'Здесь вы можете расчитать стоимость с учетом доставки и комиссии.\n'
                                   f'для подсчёта используйте команду /cost:\nТекущий курс CNY/RUB с ЦБ РФ: {date()}',
                              reply_markup=back_menu)
    elif call.data == 'option7':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Здесь вы можете оставить свой заказ, который далее будет отправлен продавцам. \n'
                                   'Форма для заказа:\n\n'
                                   'Ссылки на товары\n'
                                   'Споссоб доставки (Эконом, Стандарт, Ультра)\n\n'
                                   'Для отправки заказа используйте команду /order\n\n',
                              reply_markup=back_menu)
    elif call.data == 'back':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=hello,
                              reply_markup=keyboard)


bot.polling()
