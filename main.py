import telebot
import random
    
# Замени 'TOKEN' на токен твоего бота
# Этот токен ты получаешь от BotFather, чтобы бот мог работать
bot = telebot.TeleBot("7918813960:AAHKYzKaC29p1XLZKF4CY7F5vNbgZOm1394")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я твой Telegram бот. у меня есть команды например /battery и это подскажет куда тебе положить этот предмет если хочешь узнать все команды пиши /commands!")

@bot.message_handler(commands=['commands'])
def send_hello(message):
    bot.reply_to(message, "у меня есть комманды battery, tv, food, tiles, plastic, paper, receipt, pocket и wet paper, a также есть мемы через комманду /mem /mem1 /mem2 /animals /animals1 /animals2 и /animals3")

@bot.message_handler(commands=['hello'])
def send_hello(message):
    bot.reply_to(message, "Привет! Как дела?")

@bot.message_handler(commands=['bye'])
def send_bye(message):
    bot.reply_to(message, "Пока! Удачи!")

@bot.message_handler(commands=['cool'])
def send_cool(message):
    bot.reply_to(message, "Спасибо!")

@bot.message_handler(commands=['heh'])
def send_heh(message):
     bot.reply_to(message, "hehehehe")

@bot.message_handler(commands=['mem'])
def send_mem(message):
    with open('images/mem1.jpg', 'rb') as f:  
        bot.send_photo(message.chat.id, f)  

@bot.message_handler(commands=['mem2'])
def send_mem(message):
    with open('images/mem2.jpg', 'rb') as f:  
        bot.send_photo(message.chat.id, f)

@bot.message_handler(commands=['mem3'])
def send_mem(message):
    with open('images/mem3.jpg', 'rb') as f:  
        bot.send_photo(message.chat.id, f)

@bot.message_handler(commands=['animals'])
def send_mem(message):
    with open('images/animals.jpg', 'rb') as f:  
        bot.send_photo(message.chat.id, f)

@bot.message_handler(commands=['animals2'])
def send_mem(message):
    with open('images/animals2.jpg', 'rb') as f:  
        bot.send_photo(message.chat.id, f)

@bot.message_handler(commands=['animals3'])
def send_mem(message):
    with open('images/animals3.jpg', 'rb') as f:  
        bot.send_photo(message.chat.id, f)

@bot.message_handler(commands=['battery'])
def send_heh(message):
     bot.reply_to(message, "кидай батарейку в контейнер для батареек скорее всего он будет находиться в общественных местах и он будет маленьким ")

@bot.message_handler(commands=['tv'])
def send_heh(message):
     bot.reply_to(message, "в спец приемы для электроники")

@bot.message_handler(commands=['food'])
def send_heh(message):
     bot.reply_to(message, "в коричневый контейнер")

@bot.message_handler(commands=['tiles'])
def send_heh(message):
    bot.reply_to(message, "в серый или черный контейнер")

@bot.message_handler(commands=['plastic'])
def send_heh(message):
    bot.reply_to(message, "в желтый контейнер")
    
@bot.message_handler(commands=['paper'])
def send_heh(message):
     bot.reply_to(message, "бумагу в синий контейнер")

@bot.message_handler(commands=['wet paper'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['receipt'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")
     
bot.message_handler(commands=['teethbrush'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['pocket'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['receipt'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['receipt'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['receipt'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['receipt'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['receipt'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")

bot.message_handler(commands=['receipt'])
def send_heh(message):
     bot.reply_to(message, "в черный или серый контейнер")
     









@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()