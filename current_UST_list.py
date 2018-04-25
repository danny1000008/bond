#!/usr/bin/python
# written by Danny Wagstaff 2/2018

from flask import Flask, render_template, request
#from . import contractBasketBeta # works with development server (127.0.0.1:5000)
import contractBasket # works in production (dwagstaff.com/bondapp2)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods = ['POST'])
def index_post():
    FC = request.form['futCon'] # futures contract chosen
    listTsyData = contractBasket.Basket() # class Basket will hold UST securities list
    listTsyData.getBasket(FC)
    return render_template('CTDList.html', listData=listTsyData.value, FC = FC, mat = listTsyData.getConAbbr())

if __name__ == "__main__":
    app.run()
