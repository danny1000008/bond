#!/usr/bin/python
# written by Danny Wagstaff 2/2018

import sys, os
import urllib3
import certifi
import datetime
import json
#from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def getWebPg(sec="Note"):
    urlObj=urllib3.PoolManager(cert_reqs="CERT_REQUIRED",ca_certs=certifi.where())
    return urlObj.request("GET", "https://www.treasurydirect.gov/TA_WS/securities/search?format=json&type="+sec)

def getDlvDates(dt=datetime.date.today()):
    day1DelMth=dt
    if dt.month%3==0:   # Mar,Jun, Sep, Dec
        day1DelMth=datetime.date(dt.year,dt.month,1)
    elif dt.month%3==1: # Jan, Apr, Jul, Oct
        day1DelMth=datetime.date(dt.year,dt.month+2,1)
    else:                       # Feb, May, Aug, Nov
        day1DelMth=datetime.date(dt.year,dt.month+1,1)
    dayLastDelMth=datetime.date(day1DelMth.year,day1DelMth.month+1,1)-datetime.timedelta(days=1)
    return (day1DelMth,dayLastDelMth)

def getConAbbr(conPrefix='',dt=datetime.date.today()):
    dictFrontContract={1:"H",2:"H",3:"H",4:"M",5:"M",6:"M",7:"U",8:"U",9:"U",10:"Z",11:"Z",12:"Z"}
    return conPrefix + dictFrontContract[dt.month]+str(dt.year)[3]

def getMatDate(ustSec):
    return datetime.date(int(ustSec["maturityDate"][0:4]),int(ustSec["maturityDate"][5:7]),int(ustSec["maturityDate"][8:10]))


@app.route('/TU')
def getTUBasket():
    tsyDrct=getWebPg("Note")
    (day1DelMth,dayLastDelMth)=getDlvDates()

    '''
    TU Contract Delivery Specifications
    U.S. Treasury notes with an original term to maturity of 
    1) not more than five years and three months and a remaining term to maturity of 
    2) not less than one year and nine months from the first day of the delivery month and a remaining 
    term to maturity of 
    3) not more than two years from the last day of the delivery month. 
    '''

    dictUSTNotes=json.loads(tsyDrct.data.decode("utf-8"))
    dictUSTTerms={"2-Year":2,"3-Year":3,"5-Year":5,"7-Year":7,"9-Year 10-Month":9.8333,
      "9-Year 11-Month":9.9167,"10-Year":10,"29-Year 10-Month":29.8333,
      "29-Year 11-Month":29.9167,"30-Year":30}
    dictTUSpecs={"OrigTermMax":5.25,"TTM_Min":1.75,"TTM_Max":2}
    secCount=0
    TUBasket=[]
    listCUSIP=[]
    
    for TNote in dictUSTNotes:
        edgeCase=''
        # check to see if condition TU 1) is satisfied
        if TNote["term"] in ["2-Year","3-Year","5-Year"]:
            USTMatDate=getMatDate(TNote)
            # check to see if condition TU 2) is satisfied
            # dateutil is not available through A2 Hosting;must do something else for dateDiff1 and dateDiff2
            #dateDiff1=relativedelta(USTMatDate,day1DelMth).years+relativedelta(USTMatDate,day1DelMth).months/12+relativedelta(USTMatDate,day1DelMth).days/365.25
            dateDiff1=(USTMatDate-day1DelMth).days/365.25 # just an approximation!
            # this may include/exclude a security on the "edge"of the basket
            if (dateDiff1)>=dictTUSpecs["TTM_Min"]:
                # temporary marking of possible edge cases
                if abs(dateDiff1-dictTUSpecs["TTM_Min"])<=0.005:
                    edgeCase='**'
                # check to see if condition TU 3) is satisfied
                #dateDiff2=relativedelta(USTMatDate,dayLastDelMth).years+relativedelta(USTMatDate,dayLastDelMth).months/12+relativedelta(USTMatDate,dayLastDelMth).days/365.25
                dateDiff2=(USTMatDate-dayLastDelMth).days/365.25
                if dateDiff2<=dictUSTTerms["2-Year"]:
                    if abs(dateDiff2-dictUSTTerms["2-Year"])<=0.005:
                        edgeCase='**'
                    if len(TNote["interestRate"])>0 and not (TNote["cusip"] in listCUSIP): # must check for WI notes and reopenings
                        secCount=secCount+1
                        TTM=(USTMatDate-datetime.date.today()).days/365.25
                        TTM=str('%.2f' % TTM)
                        TUBasket.append({'matDate':TNote["maturityDate"][0:10]+edgeCase,'TTM':TTM,'intRate':float(TNote["interestRate"]),'cpnsPerYr':2,'cusip':TNote["cusip"]})
                        listCUSIP.append(TNote["cusip"])
    return TUBasket

@app.route('/FV')
def getFVBasket():
    tsyDrct=getWebPg("Note")         
    (day1DelMth,dayLastDelMth)=getDlvDates()

    '''
    FV Contract Delivery Specifications
    U.S. Treasury notes with an original term to maturity of 
    1) not more than five years and three months and a remaining term to maturity of 
    2) not less than 4 years and two months as of the first day of the delivery month. 
    '''
    dictUSTNotes=json.loads(tsyDrct.data.decode("utf-8"))
    dictFVSpecs={"OrigTermMax":5.25,"TTM_Min":4.1667,"TTM_Max":5.25}
    secCount=0
    FVBasket=[]
    listCUSIP=[]
    
    for TNote in dictUSTNotes:
        edgeCase=''
        # check to see if condition FV 1) is satisfied
        if TNote["term"] == "5-Year":
            USTMatDate=getMatDate(TNote)
            # check to see if condition FV 2) is satisfied
            # dateutil is not available through A2 Hosting;must do something else
            # for dateDiff1 and dateDiff2
            #dateDiff1=relativedelta(USTMatDate,day1DelMth).years+relativedelta(USTMatDate,day1DelMth).months/12+relativedelta(USTMatDate,day1DelMth).days/365.25
            dateDiff1=(USTMatDate-day1DelMth).days/365.25 # just an approximation!
            # this may include/exclude a security on the "edge"of the basket
            if dateDiff1>=dictFVSpecs["TTM_Min"]:
                # temporary marking of possible edge cases
                if abs(dateDiff1-dictFVSpecs["TTM_Min"])<=0.005:
                    edgeCase='**'
                # must check for WI notes and reopenings
                if len(TNote["interestRate"])>0 and not (TNote["cusip"] in listCUSIP):
                    secCount=secCount+1
                    TTM=(USTMatDate-datetime.date.today()).days/365.25
                    TTM=str('%.2f' % TTM)
                    FVBasket.append({'matDate':TNote["maturityDate"][0:10]+edgeCase,'TTM':TTM,'intRate':float(TNote["interestRate"]),'cpnsPerYr':2,'cusip':TNote["cusip"]})
                    listCUSIP.append(TNote["cusip"])
    return FVBasket

@app.route('/TY')
def getTYBasket():
    tsyDrctNote=getWebPg("Note")
    tsyDrctBond=getWebPg("Bond")    
    (day1DelMth,dayLastDelMth)=getDlvDates()
    '''
    TY Contract Delivery Specifications
    U.S. Treasury notes with an remaining term to maturity of
    1) at least 6.5 years as of the first day of the delivery month.     
    2) not more than 10 years as of the first day of the delivery month. 
    '''
    dictUSTNotes=json.loads(tsyDrctNote.data.decode("utf-8"))+json.loads(tsyDrctBond.data.decode("utf-8"))
    dictTYSpecs={"OrigTermMax":999999,"TTM_Min":6.5,"TTM_Max":10}
    secCount=0
    TYBasket=[]
    listCUSIP=[]
    
    for TNote in dictUSTNotes:
        edgeCase=''
        # check to see if condition TY 1) is satisfied
        if TNote["term"] in ["7-Year","9-Year 10-Month","9-Year 11-Month","10-Year"]:#,"29-Year 10-Month", "29-Year 11-Month","30-Year"]:
            USTMatDate=datetime.date(int(TNote["maturityDate"][0:4]),int(TNote["maturityDate"][5:7]),int(TNote["maturityDate"][8:10]))
            # check to see if condition TY 2) is satisfied
            # dateutil is not available through A2 Hosting;must do something else
            # for dateDiff1 and dateDiff2
            #dateDiff1=relativedelta(USTMatDate,day1DelMth).years+relativedelta(USTMatDate,day1DelMth).months/12+relativedelta(USTMatDate,day1DelMth).days/365.25
            dateDiff1=(USTMatDate-day1DelMth).days/365.25 # just an approximation!
            # this may include/exclude a security on the "edge"of the basket
            if (dateDiff1>=dictTYSpecs["TTM_Min"] and dateDiff1<=dictTYSpecs["TTM_Max"]):
                if abs(dateDiff1-dictTYSpecs["TTM_Min"])<=0.005:
                    edgeCase='**'
                # must check for WI notes and reopenings
                if len(TNote["interestRate"])>0 and not (TNote["cusip"] in listCUSIP):
                    secCount=secCount+1
                    TTM=(USTMatDate-datetime.date.today()).days/365.25
                    TTM=str('%.2f' % TTM)
                    TYBasket.append({'matDate':TNote["maturityDate"][0:10]+edgeCase,'TTM':TTM,'intRate':float(TNote["interestRate"]),'cpnsPerYr':2,'cusip':TNote["cusip"]})
                    listCUSIP.append(TNote["cusip"])
    return TYBasket

@app.route('/', methods=['POST'])
def index_post():
    FC=request.form['futCon']
    listTsyData=[]
    if FC=='TU':
        listTsyData=getTUBasket()
    elif FC=='FV':
        listTsyData=getFVBasket()
    else: # FC='TY'
        listTsyData=getTYBasket()
    return render_template('CTDList.html',listData=listTsyData, FC=FC,mat=getConAbbr())

if __name__=="__main__":
    app.run()
    

