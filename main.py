#!/usr/bin/python
# written by Danny Wagstaff 2/2018

from flask import Flask, render_template, request
# from . import contractBasketBeta # works with development server (127.0....)
import contract_basket  # works in production (dwagstaff.com/bondapp2)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods = ['POST'])
def index_post():
    futures_contract = request.form['futCon']  # futures contract chosen
    futures_expiration = request.form['expiration']  # expiration month
    # Can we use an f-string here to improve readability?
    listTsyData = contract_basket.Basket()  # class Basket will hold UST list
    stl = listTsyData.get_latest_settle_date()
    listTsyData.define_basket(futures_contract, futures_expiration)
    return render_template('CTDList.html', listData=listTsyData.value,
        fc = futures_contract, fe = futures_expiration, mat =
        listTsyData.get_contract_short_name(futures_contract, futures_expiration),
        stl = stl)


if __name__ == "__main__":
    # Turn debugger on so the app automatically reloads when you edit a file
    app.run(debug = True)
