from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, DATABASE
from logic import DB_Manager

bot = TeleBot(TOKEN)
manager = DB_Manager(DATABASE)
user_cart = {}  

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 
    """Привет! Это бот для заказа еды.\nИспользуй /register чтобы зарегистрироваться""")
    help(message)

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
"""
Вот команды, которые могут тебе помочь:
/start - начать работу
/help - помощь
/register - регистрация
/menu - посмотреть меню
/order - сделать заказ
/cart - посмотреть корзину
""")

@bot.message_handler(commands=['register'])
def register(message):
    user_id = message.from_user.id
    name = message.from_user.first_name 

    if manager.get_user(user_id):
        bot.send_message(message.chat.id, "Вы уже зарегистрированы!")
    else:
        manager.add_user(user_id, name, "не указан")
        bot.send_message(message.chat.id, f"Регистрация завершена, {name}!")
    show_main_menu(message.chat.id)

@bot.message_handler(commands=['menu'])
def handle_menu(message):
    show_categories(message.chat.id, "menu")

@bot.message_handler(commands=['order'])
def handle_order(message):
    show_categories(message.chat.id, "order")

@bot.message_handler(commands=['cart'])
def show_cart(message):
    markup = InlineKeyboardMarkup()
    user_id = message.chat.id
    if user_id not in user_cart or not user_cart[user_id]:
        bot.send_message(user_id, "Ваша корзина пуста.")
        return

    msg = "Ваша корзина:\n"
    total = 0
    for dish_id in user_cart[user_id]:
        all_dishes = manager.get_dishes()
        for d in all_dishes:
            if d[0] == dish_id:
                name, price = d[1], d[3]
                msg += f"{name} - {price}₽\n"
                total += price
    msg += f"\nИтого: {total}₽"
    markup.add(InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order"))
    bot.send_message(user_id, msg, reply_markup=markup)

def show_main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Меню", callback_data='show_menu'),
        InlineKeyboardButton("Заказать", callback_data='make_order')
    )
    bot.send_message(chat_id, "Главное меню:", reply_markup=markup)

def show_categories(chat_id, next_action):
    categories = manager.get_categories()
    markup = InlineKeyboardMarkup()
    for cat_id, name, image_url in categories:
        markup.add(InlineKeyboardButton(name, callback_data=f"{next_action}_cat_{cat_id}"))
    bot.send_photo(chat_id, photo=open('images/menu.jpg', 'rb'), caption="Выберите категорию:", reply_markup=markup)



def show_food_menu(chat_id, category_id):
    categories = manager.get_categories()
    category_image_url = next((img for cid, _, img in categories if cid == category_id), None)
    if category_image_url:
        bot.send_photo(chat_id, open(category_image_url, 'rb'))

    dishes = manager.get_dishes(category_id)
    if not dishes:
        bot.send_message(chat_id, "В этой категории пока нет блюд.")
        return

    markup = InlineKeyboardMarkup()
    for dish in dishes:
        dish_id, name, desc, price, *_ = dish
        markup.add(InlineKeyboardButton(f"{name} - {price}₽", callback_data=f"order_{dish_id}"))

    markup.add(InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order"))
    bot.send_message(chat_id, "Выберите блюда (можно несколько):", reply_markup=markup)

def choose_food(chat_id, category_id):
    show_food_menu(chat_id, category_id)

def add_to_cart(chat_id, dish_id):
    user_id = chat_id
    if user_id not in user_cart:
        user_cart[user_id] = []
    user_cart[user_id].append(dish_id)

    dish = next((d for d in manager.get_dishes() if d[0] == dish_id), None)
    if dish:
        name, desc, price, _, _, image_url = dish[1:7]
        if image_url:
            bot.send_photo(chat_id, open(image_url, 'rb'))
        bot.send_message(chat_id, f"Добавлено в заказ: {name} ({price}₽)")



def confirm_order(chat_id):
    user_id = chat_id
    if user_id not in user_cart or not user_cart[user_id]:
        bot.send_message(chat_id, "Ваша корзина пуста.")
        return

    items = user_cart[user_id]
    order_id = manager.create_order_with_items(user_id, items)

    message_lines = []
    total = 0
    all_dishes = manager.get_dishes()
    for dish_id in items:
        for d in all_dishes:
            if d[0] == dish_id:
                name, price = d[1], d[3]
                total += price
                message_lines.append(f"{name} - {price}₽")

    msg = "Ваш заказ:\n" + "\n".join(message_lines) + f"\n\nИтого: {total}₽"
    bot.send_message(chat_id, msg)
    user_cart[user_id] = []
    bot.send_message(chat_id, f"Заказ №{order_id} успешно оформлен! Ожидайте доставку.")
    show_main_menu(chat_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'show_menu':
        show_categories(call.message.chat.id, "menu")
    elif call.data == 'make_order':
        show_categories(call.message.chat.id, "order")
    elif call.data.startswith('menu_cat_'):
        category_id = int(call.data.replace('menu_cat_', ''))
        show_food_menu(call.message.chat.id, category_id)
    elif call.data.startswith('order_cat_'):
        category_id = int(call.data.replace('order_cat_', ''))
        choose_food(call.message.chat.id, category_id)
    elif call.data.startswith('order_'):
        dish_id = int(call.data.replace('order_', ''))
        add_to_cart(call.message.chat.id, dish_id)
    elif call.data == 'confirm_order':
        confirm_order(call.message.chat.id)

if __name__ == '__main__':
    manager.create_database()
    bot.infinity_polling()
