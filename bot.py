from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
from config import TOKEN, DATABASE
from logic import DB_Manager

bot = TeleBot(TOKEN)

def show_main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Меню", callback_data='show_menu'),
        InlineKeyboardButton("Заказать", callback_data='make_order')
    )
    bot.send_message(chat_id, "Главное меню:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 
    """Привет! Это бот для заказа еды.
Используй /register чтобы зарегистрироваться""")
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
    show_food_menu(message.chat.id)

@bot.message_handler(commands=['order'])
def handle_order(message):
    choose_food(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'show_menu':
        show_food_menu(call.message.chat.id)
    elif call.data == 'make_order':
        choose_food(call.message.chat.id)
    elif call.data.startswith('order_'):
        dish_id = int(call.data.replace('order_', ''))
        confirm_order(call.message.chat.id, dish_id)

def show_food_menu(chat_id):
    dishes = manager.get_dishes()
    if not dishes:
        bot.send_message(chat_id, "Меню пока пустое.")
        return

    markup = InlineKeyboardMarkup()
    for dish in dishes:
        dish_id, name, desc, price, *_ = dish
        markup.add(InlineKeyboardButton(f"{name} - {price}₽", callback_data=f"order_{dish_id}"))
    
    bot.send_message(chat_id, "Выберите блюдо из меню:", reply_markup=markup)

def choose_food(chat_id):
    show_food_menu(chat_id)

def confirm_order(chat_id, dish_id):
    dish = next((d for d in manager.get_dishes() if d[0] == dish_id), None)
    if dish:
        name, price = dish[1], dish[3]
        bot.send_message(chat_id, f"Ваш заказ '{name}' ({price}₽) принят! Ожидайте доставку.")
    else:
        bot.send_message(chat_id, "Блюдо не найдено.")
    
    show_main_menu(chat_id)

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.infinity_polling()

