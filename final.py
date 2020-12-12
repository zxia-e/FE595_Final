from flask import Flask, request, render_template, jsonify, Response
import numpy as np


app = Flask(__name__)

class StockPriceSimulator():
    # assume the stock price follow geometric brownian motion, get the terminal price
    @staticmethod
    def simulate_ST(S0, r, sigma, T):
        Z = np.random.randn()
        return S0 * np.exp((r - 0.5 * sigma * sigma) * T + sigma * np.sqrt(T) * Z)

    # assume the stock price follow geometric brownian motion, get whole path
    @staticmethod
    def simulate_whole_path(S0, r, sigma, T, N):
        norms = np.random.randn(N)  # Z
        path = np.zeros(N)
        dt = float(T) / N  # interval

        path[0] = S0
        for i in range(1, N):
            path[i] = path[i - 1] * np.exp(
                (r - 0.5 * sigma * sigma) * dt + sigma * np.sqrt(dt) * norms[i])  # price at time [i]

        return path


#Asian Option Pricer Call
class AsianOptionPricerCall():
    def price(self, K, S0, r, sigma, T, N, scnario):  # K = strike
        prices = np.zeros(scnario)
        for i in range(scnario):
            stock_path = StockPriceSimulator.simulate_whole_path(S0, r, sigma, T, N)
            prices[i] = np.exp(-r * T) * self.pay_off(stock_path, K)  # price at time 0
        return prices.mean()

    def pay_off(self, stock_path, K):
        return stock_path.mean() - K

#European Option PricerCall
class EuropeanOptionPricerCall():
    def price(self, K, S0, r, sigma, T, N, scnario):
        prices = np.zeros(scnario)
        for i in range(scnario):
            stock_path = StockPriceSimulator.simulate_whole_path(S0, r, sigma, T, N)
            prices[i] = np.exp(-r * T) * self.pay_off(stock_path, K)
        return prices.mean()

    def pay_off(self, stock_path, K):
        return stock_path[-1] - K



@app.route('/')
def home():
    return render_template('request.html')

@app.route('/join', methods=['GET','POST'])
def my_form_post():
    strike_price = float(request.form['text1'])
    start_price = float(request.form['text2'])
    rate = float(request.form['text3'])
    sigma = float(request.form['text4'])
    time = int(request.form['text5'])
    interval = int(request.form['text6'])
    scnario = int(request.form['text7'])
    option_choice = request.form['text8']
    # sim = StockPriceSimulator.simulate_whole_path()

    if option_choice.lower() == 'asian':
        combine =AsianOptionPricerCall()
        result = {"output": combine.price(strike_price,start_price, rate, sigma, time,interval, scnario)}
        result ={str(key): value for key, value in result.items()}
        return jsonify(result = result)

    elif option_choice.lower() == 'european':
        combine = EuropeanOptionPricerCall()
        result = {"output": combine.price(strike_price,start_price, rate, sigma, time,interval, scnario)}
        result = {str(key): value for key, value in result.items()}
        return jsonify(result=result)

    else:
        print("400 Bad request")
        return jsonify(result = "Not Found"),400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    #app.run()