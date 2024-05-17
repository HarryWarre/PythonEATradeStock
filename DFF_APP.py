from flask import Flask, render_template, request, jsonify
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    selected_pair = request.form['currency_pair']
    try:
        yesterday = datetime.now() - timedelta(1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        data = yf.download(selected_pair, start=yesterday_str, interval='60m')
        data = data.dropna()

        model = load_model('dff_forex.h5')

        data['EMA'] = data['Close'].ewm(span=21, adjust=False).mean()
        delta = data['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        data['AU'] = gain.rolling(window=14, min_periods=1).mean()
        data['AD'] = loss.rolling(window=14, min_periods=1).mean()
        data['RSI'] = calculate_rsi(data)
        data['ERSI'] = calculate_ersi(data['RSI'])

        scaler = StandardScaler()
        features = ['EMA', 'AU', 'AD']
        X = scaler.fit_transform(data[features])

        predicted_classes = np.argmax(model.predict(X), axis=1)
        market_states = ['Downtrend', 'Uptrend', 'Sideway']
        predicted_labels = [market_states[i] for i in predicted_classes]
        data['Market_State'] = predicted_labels

        fig, ax = plt.subplots()

        filtered_data = data.loc['2023-05-15':]
        market_states = filtered_data[["RSI", "ERSI", "Market_State"]]
        current_market_state = None

        ax.plot(filtered_data.index, filtered_data['Close'], color='black', label='Close')
        ax.plot(filtered_data.index, filtered_data['EMA'], color='blue', label='EMA')

        for index, row in market_states.iterrows():
            rsi = row['RSI']
            ersi = row['ERSI']
            market_state = row['Market_State']
            if market_state != current_market_state:
                current_market_state = market_state
                if condition_buy(rsi, ersi, market_state):
                    color = 'green'
                    ax.scatter(index, filtered_data.loc[index, 'Low'], color=color, marker='o')
                if condition_sell(rsi, ersi, market_state):
                    color = 'red'
                    ax.scatter(index, filtered_data.loc[index, 'Low'], color=color, marker='o')

        for index, row in market_states.iterrows():
            market_state = row['Market_State']
            current_market_state = market_state
            if market_state == "Uptrend": color = 'blue'
            else: color = 'purple'
            ax.scatter(index, filtered_data.loc[index, 'High'], color=color, marker='o')

        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()

        # Convert plot to PNG image
        img = io.BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')

        last_row = data.iloc[-1]
        if condition_buy(last_row['RSI'], last_row['ERSI'], last_row['Market_State']):
            result = 'Buy'
        else:
            result = 'Not buy this time'

        return jsonify({'result': result, 'plot_url': plot_url})
    except Exception as e:
        return jsonify({'error': str(e)})

def condition_buy(rsi, ersi, market_state):
    return (rsi > ersi) and (market_state == 'Uptrend') and (ersi > 40 or ersi < 60)

def condition_sell(rsi, ersi, market_state):
    return (rsi < ersi) and (market_state == 'Downtrend') and (ersi > 40 or ersi < 60)

def calculate_rsi(data, window=14):
    close = data['Close']
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_ersi(rsi, window=14):
    ersi = rsi.ewm(span=window, min_periods=0, adjust=False).mean()
    return ersi
if __name__ == '__main__':
    app.run(debug=True)
