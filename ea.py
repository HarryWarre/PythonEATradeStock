from datetime import date
import talib
import pandas as pd
from api import get_stock_data, list_companies
from orders import Order, OrdersManager
from datetime import datetime, timedelta

class Strategy:
    def __init__(self):
        self.orders_manager = OrdersManager()

    def execute_buy_strategy(self, symbol, buy_price, stop_loss, date):
        # Kiểm tra và đặt lệnh mua mới
        if not self.orders_manager.check_existing_order(symbol):
            self.orders_manager.place_order(symbol, buy_price, stop_loss, date)

    def execute_exit_strategy(self, symbol):
        print(symbol)
        # Kiểm tra và thoát lệnh mua
        if self.orders_manager.check_existing_order(symbol):
            # Xóa lệnh
            self.orders_manager.remove_order(symbol)
            # Thực hiện thoát lệnh ở đây (ví dụ: xóa lệnh khỏi danh sách)
            print(f"Đã thoát lệnh cho {symbol}")
        else:
            print(f"Mã cổ phiếu {symbol} không tồn tại trong danh sách lệnh")

    def update_trailing_stop_loss(self):
        # Đọc danh sách các mã cổ phiếu từ file
        symbols = []
        with open('orders.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(', ')
                symbol = parts[0].split(': ')[1]  # Lấy phần tử sau dấu hai chấm từ phần tách được
                order_day = datetime.strptime(parts[3].split(': ')[1], '%Y-%m-%d %H:%M:%S') #Date order
                days_difference = (datetime.now() - order_day).days

                if int(days_difference) > 3:  # Kiểm tra số ngày vào lệnh
                    symbols.append(symbol)

        # Duyệt qua từng mã cổ phiếu và kiểm tra cập nhật trailing stop loss
        for symbol in symbols:
            df = self.calculate_technical_indicators(symbol)  # Lấy DataFrame cho mã cổ phiếu hiện tại
            self.check_and_update_trailing_stop_loss(df)

    def check_and_update_trailing_stop_loss(self, df):
        # Lấy ngày hiện tại
        current_date = datetime.now()
        # Lấy ngày 1 tuần trước
        start_date = (current_date - timedelta(days=7)).strftime('%Y-%m-%d')

        # Lấy dữ liệu chỉ số kỹ thuật từ tuần gần đây
        recent_indicator_data = df[start_date:current_date.strftime('%Y-%m-%d')]

        # Lấy giá trị stoploss cuối cùng trong tuần gần đây
        max_stop_loss = 0
        
        for index, row in recent_indicator_data.iterrows():
            stop_loss = round(row['close'] - row['atr'] * 1.5, 2)
            print(index, 'Price: ', row['close'])
            print('SL: ', stop_loss)
            if max_stop_loss is None or stop_loss > max_stop_loss:
                max_stop_loss = stop_loss
            print('Max sl: ', max_stop_loss)
        # Đọc file txt để kiểm tra các lệnh và cập nhật trailing stop loss
        with open('orders.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                parts = line.split(',')
                symbol = parts[0]
                stop_loss_from_txt = round(float(parts[2].split(':')[1].strip()),2)
                
                # Kiểm tra nếu stop loss mới lớn hơn stop loss từ file
                if max_stop_loss > stop_loss_from_txt:
                    self.orders_manager.update_stop_loss(symbol, max_stop_loss, current_date)
                    print(f"Đã cập nhật trailing stop loss cho {symbol} thành {max_stop_loss}")

    def calculate_technical_indicators(self, in_symbol):
        # Lấy ngày hiện tại
        current_date = datetime.now().strftime('%Y-%m-%d')
        # Lấy ngày 7 ngày trước
        start_date = (datetime.now() - timedelta(days=50)).strftime('%Y-%m-%d')
        
        # Lấy dữ liệu chứng khoán từ hàm get_stock_data
        data = get_stock_data(symbol=in_symbol,
                            start_date=start_date,
                            end_date=current_date,
                            data_source="VND")

        # Calculate the indicators
        data['rsi'] = talib.RSI(data['close'], timeperiod=14)
        data['upper_band'], data['middle_band'], data['lower_band'] = talib.BBANDS(data['close'], timeperiod=10, nbdevup=2, nbdevdn=2)
        data['atr'] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14)
        data['atr_prev'] = data['atr'].shift(1)
        data['aroon_osc'] = talib.AROONOSC(data['high'], data['low'], timeperiod=18)
        data['volume_prev'] = data['volume'].shift(1)
        return data

    # Buying shares conditions
    def check_buy_signals(self, df, symbol):
        orders_manager = OrdersManager()
        list_signal = []

        current_date = datetime.now()
        start_date = (current_date - timedelta(days=7)).strftime('%Y-%m-%d')

        recent_data = df[start_date:current_date.strftime('%Y-%m-%d')]

        for index, row in recent_data.iterrows():
            stoploss_price = row['close'] - row['atr'] * 1.5 
            # Entry Condition
            if (
                    (
                        (row['close'] > row['upper_band']) and
                        (row['atr'] > row['atr_prev']) and
                        (row['rsi'] > 30) and
                        (row['volume'] > row['volume_prev']) and
                        (row['aroon_osc'] > -80)
                    )
                ):
                if (row['close'] > round(stoploss_price, 2) ) :
                    list_signal.append(f"Buy {symbol} giá {row['close']} với Stoploss {round(stoploss_price, 2) }")
                    orders_manager.place_order(symbol, row['close'], round(stoploss_price), index)  # Đặt lệnh mua

        return list_signal


strategy = Strategy()
strategy.update_trailing_stop_loss()