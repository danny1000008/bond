#!/usr/bin/python
# written by Danny Wagstaff 2/2018

from flask import Flask, render_template, request
#from . import contractBasketBeta # works with development server (127.0.0.1:5000)
import contract_basket # works in production (dwagstaff.com/bondapp2)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods = ['POST'])
def index_post():
    fc = request.form['futCon'] # futures contract chosen
    fe = request.form['expiration'] # expiration month
    # Can we use an f-string here to improve readability?
    listTsyData = contract_basket.Basket() # class Basket will hold UST securities list
    stl = listTsyData.get_latest_stl_date()
    listTsyData.define_basket(fc, fe)
    return render_template('CTDList.html', listData=listTsyData.value, fc = fc,
        fe = fe, mat = listTsyData.get_contract_short_name(fc, fe), stl = stl)

if __name__ == "__main__":
    # Turn debugger on so the app automatically reloads when you edit a file
    app.run(debug = True)
