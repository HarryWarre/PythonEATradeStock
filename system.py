# This file will controll and use EAs. 
# System will have functions packaging from strategies file
from ea import Strategy  
from api import get_stock_data, list_companies

strategy = Strategy()

class SystemController:
    #Sort Stock from HOUSE with buy conditions
    def sort_buy(self):
        symbols = list_companies()
        for symbol in symbols:
            try:
                df = strategy.calculate_technical_indicators(symbol)
                signals = strategy.check_buy_signals(df, symbol)
                print(signals)
            except Exception as e:
                print(f"Lỗi xảy ra")
    # Run System
    def execute_trade_cycle (self): 
        # self.sort_buy()
        strategy.update_trailing_stop_loss()

    #Print orders list:
    def print_order_info(self):
        with open('orders.txt', 'r') as file:
            lines = file.readlines()
            for index, line in enumerate(lines, start=1):
                parts = line.strip().split(', ')
                symbol = parts[0].split(': ')[1]
                buy_price = parts[1].split(': ')[1]
                stop_loss = parts[2].split(': ')[1]
                print(f"{index}. Symbol: {symbol} - Giá mở: {buy_price} - SL: {stop_loss}")