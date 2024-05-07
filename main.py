import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Updater
import logging
import pandas as pd

print('Starting bot ... ')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Đọc dữ liệu từ file và chuyển thành một danh sách các tuple (index, symbol, buy_price, stop_loss)
    data = []
    with open('orders.txt', 'r') as file:
        for index, line in enumerate(file, start=1):
            parts = line.strip().split(', ')
            symbol = parts[0].split(': ')[1]
            buy_price = float(parts[1].split(': ')[1])  # Chuyển đổi thành số thực
            stop_loss = float(parts[2].split(': ')[1])
            data.append((index, symbol, buy_price, stop_loss))
    
    # Lọc ra các dòng có giá từ 15 đến 25 và sắp xếp theo giá mở tăng dần
    filtered_data = [(index, symbol, buy_price, stop_loss) for index, symbol, buy_price, stop_loss in data if 15 <= float(buy_price) <= 25]
    sorted_data = sorted(filtered_data, key=lambda x: x[2])
    
    # In ra top 20 dòng
    count = 0
    for index, symbol, buy_price, stop_loss in sorted_data:
        count += 1
        print(f"{index}. Symbol: {symbol} - Giá mở: {buy_price} - SL: {stop_loss}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{index}. Symbol: {symbol} - Giá mở: {buy_price} - SL: {stop_loss}")
        if count >= 20:
            break



if __name__ == '__main__':
    application = ApplicationBuilder().token('7041140079:AAGL9uu-zgqnw26Qxx9yeGt01NNcrtpNz5g').build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    application.run_polling()