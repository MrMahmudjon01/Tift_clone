from telegram import Bot
from telegram.ext import Updater
from telegram.ext import Dispatcher, CommandHandler
from apps.telegram.handlers import commands





BOT_TOKEN = "***REMOVED_BOT_TOKEN***"
bot = Bot(token=BOT_TOKEN)

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", commands.start))
dispatcher.add_handler((CommandHandler("help", commands.help)))
