#!/usr/bin/python
# written by Danny Wagstaff 2/2018

from flask import Flask, render_template, request
from . import contractBasket

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    FC=request.form['futCon']
    listTsyData=contractBasket.Basket()
    if FC=='TU':
        listTsyData.getTUBasket()
    elif FC=='FV':
        listTsyData.getFVBasket()
    else: # FC='TY'
        listTsyData.getTYBasket()
    return render_template('CTDList.html',listData=listTsyData.value, FC=FC,mat=listTsyData.getConAbbr())

if __name__=="__main__":
    app.run()