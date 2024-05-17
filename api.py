import vnquant.data as dt
import pandas as pd
from vnstock import *
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def get_stock_data(symbol, start_date, end_date, data_source):
    # Tải dữ liệu chứng khoán
    loader = dt.DataLoader(symbols=symbol,
                           start=start_date,
                           end=end_date,
                           minimal=True,
                           data_source=data_source)
    data = loader.download()
    data = data.stack()
    data = data.reset_index()
    data = data.set_index('date')
    return data

def list_companies():
    # Sử dụng hàm listcompanies để lấy dữ liệu từ API
    data = listing_companies()

    # Tạo DataFrame từ dữ liệu trả về
    df = pd.DataFrame(data)

    # Lọc dữ liệu để chỉ giữ lại các mã từ sàn HOSE
    symbols_hose = df[df['comGroupCode'] == 'HOSE']['ticker'].tolist()

    return symbols_hose