# DFF_forex
# Thực hiện chiến lược DFF, sử dụng mô hình DFF.h5

# %% [markdown]
# Thực hiện get data thị trường chứng khoán việt nam

# %%
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
import numpy as np
import talib as ta
import pandas as pd
import yfinance as yf


# Tải dữ liệu giá cổ phiếu MSFT từ 1/1/2020 đến ngày hiện tại
data = yf.download('NZDCAD=X', start='2024-05-15', interval='30m')

# %%
data.dropna()

# %% [markdown]
# Thực hiện tính các indicator cần thiết

# %%
# Tải mô hình đã được lưu trước
model = load_model('dff_forex.h5')

# Tính toán các chỉ số kỹ thuật (EMA, AU, AD)
data['EMA'] = data['Close'].ewm(span=21, adjust=False).mean()
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
data['AU'] = gain.rolling(window=14, min_periods=1).mean()
data['AD'] = loss.rolling(window=14, min_periods=1).mean()
#Tính toán thêm các indicator khác:
data['RSI'] = ta.RSI(data['Close'], timeperiod=14)
data['ERSI'] = ta.EMA(data['RSI'], timeperiod=14)
# %% [markdown]
# Thực hiện thêm mô hình

# %%
# Chuẩn hóa dữ liệu
scaler = StandardScaler()
features = ['EMA', 'AU', 'AD']
X = scaler.fit_transform(data[features])

# Dự đoán trạng thái thị trường
predicted_classes = np.argmax(model.predict(X), axis=1)

# Chuyển đổi trạng thái thị trường thành các label tương ứng
market_states = ['Downtrend', 'Uptrend', 'Sideway']
predicted_labels = [market_states[i] for i in predicted_classes]

data['Market_State'] = predicted_labels

# %% [markdown]
# Kiểm  tra thử trạng thái thị trường

# %%
for i, (index, row) in enumerate(data.iterrows()):
    # In ra trạng thái thị trường và ngày tương ứng
    print(f"Date: {index}, Market State: {predicted_labels[i]}")

# %% [markdown]
# Thực hiện kiểm tra điều kiện vào lệnh, tính toán các indicator thêm:

# %%
data.dropna()

# %%
# Đặt lại tên chỉ mục
data.index.name = 'Date'

# Chuyển đổi chỉ mục từ text sang datetime
data.index = pd.to_datetime(data.index, format='%Y-%m-%d')

# Lấy năm và tháng hiện tại
current_year = pd.Timestamp.now().year
current_month = pd.Timestamp.now().month

# Lọc dữ liệu của tháng hiện tại
data_current_month = data[(data.index.year == current_year) & (data.index.month == current_month)]

# Loại bỏ các dòng có giá trị NaN
data_current_month = data_current_month.dropna()

# In toàn bộ dữ liệu của tháng hiện tại
print(data_current_month)

# %% [markdown]
# Thực hiện kiểm tra điều kiện hiện tại:

# %%
# print(data.last)

last_row = data.iloc[-1]
if(
    (last_row['RSI'] > last_row['ERSI'])
    and (last_row['Market_State'] == 'Uptrend')
    and (last_row['ERSI'] > 40 or last_row['ERSI'] < 60)
):
    print('buy')
else: print('Not buy this time')
last_row

def condition_buy(rsi, ersi, market_state):
    if ((rsi > ersi)
    and (market_state == 'Uptrend')
    and (ersi > 40 or ersi < 60)):
        return True
    else: return False

def condition_sell(rsi, ersi, market_state):
    if ((rsi< ersi)
    and (market_state == 'Downtrend')
    and (ersi > 40 or ersi < 60)):
        return True
    else: return False

# %%
import pandas as pd
import matplotlib.pyplot as plt

# Lọc dữ liệu từ năm
filtered_data = data.loc['2023-05-15':]
filtered_data

# Lấy giá trị của trạng thái thị trường
market_states = filtered_data[["RSI", "ERSI", "Market_State"]]
# Tạo một biến để lưu trữ trạng thái hiện tại của thị trường
current_market_state = None

# Vẽ biểu đồ nến
filtered_data['Close'].plot(figsize=(10, 6), color='black')
filtered_data['EMA'].plot(figsize=(10, 6), color='blue')

for index, row in market_states.iterrows():
    rsi = row['RSI']
    ersi = row['ERSI']
    market_state = row['Market_State']
    if market_state != current_market_state:
        current_market_state = market_state
        if(condition_buy(rsi , ersi, market_state) ):
            color = 'green'
            plt.scatter(index, filtered_data.loc[index, 'Low'], color=color, marker='o')
        if(condition_sell(rsi , ersi, market_state) ):
            color = 'red'
            plt.scatter(index, filtered_data.loc[index, 'Low'], color=color, marker='o')

for index, row in market_states.iterrows():
    market_state = row['Market_State']
    current_market_state = market_state
    if(market_state == "Uptrend"): color = 'blue' 
    else: color = 'purple'
    
    plt.scatter(index, filtered_data.loc[index, 'High'], color=color, marker='o')

# Đặt tiêu đề và nhãn trục
plt.xlabel('Date')
plt.ylabel('Price')

# Hiển thị chú thích
plt.legend()

# Hiển thị biểu đồ
plt.show()