from queue import Queue
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater
import logging
import pandas as pd
from system import SystemController

print('Starting bot ... ')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('orders.txt', 'r') as file:
                lines = file.readlines()
                for index, line in enumerate(lines, start=1):
                    parts = line.strip().split(', ')
                    symbol = parts[0].split(': ')[1]
                    buy_price = parts[1].split(': ')[1]
                    stop_loss = parts[2].split(': ')[1]
                    print(f"{index}. Symbol: {symbol} - Giá mở: {buy_price} - SL: {stop_loss}")
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{index}. Symbol: {symbol} - Giá mở: {buy_price} - SL: {stop_loss}")

if __name__ == '__main__':
    application = ApplicationBuilder().token('7041140079:AAGL9uu-zgqnw26Qxx9yeGt01NNcrtpNz5g').build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()