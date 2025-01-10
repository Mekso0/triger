import telebot
import os

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
BOT_TOKEN = "7955555844:AAFFcsqeQ6-W0kyKKNtJNPdmvm4xmoVMWNY"

# Замените YOUR_ADMIN_ID на ID админа бота
ADMIN_ID = 6646133212

bot = telebot.TeleBot(BOT_TOKEN)
triggers = {}  # Словарь для хранения триггеров {chat_id: {trigger_word: reply_message_id}}

# Функция для сохранения триггеров в файл
def save_triggers():
    with open("triggers.txt", "w") as f:
        for chat_id, chat_triggers in triggers.items():
            for trigger, reply_id in chat_triggers.items():
                f.write(f"{chat_id}:{trigger}:{reply_id}\n")

# Функция для загрузки триггеров из файла
def load_triggers():
    if not os.path.exists("triggers.txt"):
        return {}
    with open("triggers.txt", "r") as f:
        for line in f:
            try:
                parts = line.strip().split(":", 2)
                if len(parts) == 3:
                    chat_id, trigger, reply_id = parts
                    chat_id = int(chat_id)
                    if chat_id not in triggers:
                        triggers[chat_id] = {}
                    triggers[chat_id][trigger] = int(reply_id)
                else:
                    print(f"Некорректная строка в triggers.txt: {line.strip()}")
            except ValueError as e:
                print(f"Ошибка разбора строки: {line.strip()}, ошибка: {e}")
    return triggers

# Загрузка триггеров при запуске бота
triggers = load_triggers()

def is_admin(user_id):
    return user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Пр, я бот помощник для чата\nt.me/madimods_chat")

@bot.message_handler(commands=['help'])
def send_help(message):
    chat_id = message.chat.id
    help_message = "список триггеров в этом чате:\n"
    if chat_id in triggers and triggers[chat_id]:
      for trigger in triggers[chat_id]:
        help_message+= f"- {trigger}\n"
    else:
      help_message += "нет созданных триггеров."
    bot.reply_to(message, help_message)


@bot.message_handler(commands=['trg'])
def handle_trigger_command(message):
    if not is_admin(message.from_user.id):
      bot.reply_to(message, "у вас нкт прав для  выполнения команды")
      return

    if not message.reply_to_message:
        bot.reply_to(message, "сделац реплайн на файл или напиши чо нибудь почле команды /trg")
        return

    if not message.text or len(message.text.split()) < 2:
      bot.reply_to(message, "сделац реплайн на файл или напиши чо нибудь почле команды /trg")
      return
      
    trigger_text = message.text.split(maxsplit=1)[1].strip()
    chat_id = message.chat.id
    reply_message_id = message.reply_to_message.message_id

    if chat_id not in triggers:
      triggers[chat_id] = {}

    triggers[chat_id][trigger_text] = reply_message_id

    save_triggers()
    bot.reply_to(message, f"триггер '{trigger_text}' создан")

@bot.message_handler(commands=['del'])
def handle_delete_trigger(message):
    if not is_admin(message.from_user.id):
      bot.reply_to(message, "у вас нкт прав для  выполнения команды")
      return

    if not message.text or len(message.text.split()) < 2:
        bot.reply_to(message, "укажи триггер для удаления после команды /del")
        return

    trigger_to_delete = message.text.split(maxsplit=1)[1].strip()
    chat_id = message.chat.id

    if chat_id in triggers and trigger_to_delete in triggers[chat_id]:
        del triggers[chat_id][trigger_to_delete]
        save_triggers()
        bot.reply_to(message, f"триггер '{trigger_to_delete}' удален")
    else:
        bot.reply_to(message, "")

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            bot.send_message(message.chat.id, "👋")
            bot.send_message(message.chat.id, "Пиши /help что бы узнать триггеры")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text_message(message):
  chat_id = message.chat.id
  if chat_id in triggers:
    for trigger_text, reply_message_id in triggers[chat_id].items():
       if trigger_text.lower() in message.text.lower():
          try:
            bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=reply_message_id)
          except:
            bot.reply_to(message, "файл удален")
          return

bot.polling(none_stop=True)