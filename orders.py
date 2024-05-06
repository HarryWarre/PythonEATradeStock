import datetime


class Order:
    def __init__(self, symbol, buy_price, stop_loss, date):
        self.symbol = symbol  # Mã cổ phiếu
        self.buy_price = buy_price  # Giá mua
        self.stop_loss = stop_loss  # Giá dừng lỗ
        self.date = date


class OrdersManager:
    def __init__(self):
        self.orders = []  # Danh sách các lệnh

    def place_order(self, symbol, buy_price, stop_loss, date):
        # Kiểm tra xem mã cổ phiếu đã có trong danh sách lệnh hay chưa
        if not self.check_existing_order(symbol):
            order = Order(symbol, buy_price, stop_loss, date)  # Thêm ngày hiện tại vào thông tin lệnh
            self.orders.append(order)
            self.save_orders_to_file()
            print(f"Đặt lệnh thành công cho {symbol} với giá mua {buy_price} và dừng lỗ {stop_loss}")
        else:
            print(f"Mã cổ phiếu {symbol} đã tồn tại trong danh sách lệnh")


    def remove_order(self, symbol):
        # Tạo một danh sách tạm thời để lưu các dòng cần giữ lại
        updated_lines = []
        symbol_exists = False
        print('SYMBOLS:' + symbol)
        # Mở file và kiểm tra các dòng
        with open("orders.txt", "r") as file:
            lines = file.readlines()
            print(lines)
            for line in lines:
                parts = line.strip().split(', ')
                symbol_from_file = parts[0].split(': ')[1].strip()  # Lấy phần tử sau dấu hai chấm từ phần tách được
                # Kiểm tra nếu symbol khớp với symbol được truyền vào và dòng không nên bị xóa
                if symbol_from_file != symbol:
                    updated_lines.append(line)
                else:
                    symbol_exists = True

        # Ghi lại danh sách mới vào tệp tin
        with open("orders.txt", "w") as file:
            for line in updated_lines:
                file.write(line)

        if symbol_exists:
            print(f"Đã xóa lệnh cho {symbol} khỏi danh sách")
        else:
            print(f"Mã cổ phiếu {symbol} không tồn tại trong danh sách lệnh")



    def update_stop_loss(self, symbol, new_stop_loss, day):
        # Đường dẫn tới file chứa các lệnh
        file_path = 'orders.txt'
        
        # Mở file văn bản để đọc
        with open(file_path, 'r') as file:
            # Đọc từng dòng trong file
            symbol = symbol.strip().split(': ')[1]
            lines = file.readlines()
            
            # Duyệt qua từng dòng
            for index, line in enumerate(lines):
                # Tách dòng thành các phần
                parts = line.strip().split(',')
                
                # Lấy symbol từ dòng hiện tại
                current_symbol = parts[0].split(': ')[1]

                # Kiểm tra xem symbol hiện tại có trùng khớp với symbol cần cập nhật hay không
                if current_symbol == symbol:
                    # Thay đổi stop loss trong dòng hiện tại
                    formatted_date = day.strftime('%Y-%m-%d %H:%M:%S')
                    lines[index] = f"Symbol: {symbol}, Buy Price: {parts[1].split(': ')[1]}, Stop Loss: {new_stop_loss}, Date: {formatted_date}\n"
                    
                    # Ghi lại các dòng đã được cập nhật
                    with open(file_path, 'w') as file:
                        file.writelines(lines)
                    
                    print(f"Đã cập nhật trailing stop loss cho {symbol} thành {new_stop_loss}")
               
                    break
            else:
                print(f"Lệnh {symbol} không tồn tại trong danh sách lệnh")

    def check_existing_order(self, symbol):
        # Mở file và kiểm tra các dòng
        with open("orders.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(', ')
                symbol_from_file = parts[0].split(': ')[1].strip()  # Lấy phần tử sau dấu hai chấm từ phần tách được
                if symbol_from_file == symbol:
                    return True
        return False


    def save_orders_to_file(self):
        # Đọc dữ liệu hiện có từ file
        existing_data = []
        with open("orders.txt", "r") as file:
            existing_data = file.readlines()

        # Ghi dữ liệu mới vào file
        with open("orders.txt", "w") as file:
            # Ghi dữ liệu hiện có trở lại file
            for line in existing_data:
                file.write(line)
            
            # Ghi danh sách lệnh mới
            for order in self.orders:
                file.write(f"Symbol: {order.symbol}, Buy Price: {order.buy_price}, Stop Loss: {order.stop_loss}, Date: {order.date}\n")

