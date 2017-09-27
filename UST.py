#!/usr/bin/env
# written by Danny Wagstaff 9/2017
import bond
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class UST(bond):
    def __init__(self,cpn,cpnFreq):
        self.cpn=cpn
        self.cpnFreq=cpnFreq
        
    def numCoupons(self, basis):
        cpnIndex=0
        tempDate=self.nextCpn(self.stlDate)
        while tempDate <= self.matDate:
            cpnIndex+=1
            tempDate=self.nextCpn(tempDate)
        return cpnIndex
    
    def prevCpn(self,startDate):
        # 1st guess for next coupon date is maturity date
        tempCpnDate=self.matDate
        flagEndOfMonth=None # Use this to ID a matDate that is the last day of the month
                            # We need this to make sure nextCpn returns a date that is the last day
                            # of the month returned
        if (self.matDate+timedelta(days=1)).day==1:
            flagEndOfMonth=1
        while tempCpnDate-startDate > timedelta(days=0):
            tempCpnDate=tempCpnDate-relativedelta(months=6)
        if flagEndOfMonth:
            # get 1st day of next month after coupon payment
            day1OfNextMo=tempCpnDate+relativedelta(months=1)
            day1OfNextMo=date(day1OfNextMo.year,day1OfNextMo.month,1)
            while day1OfNextMo - tempCpnDate > timedelta(days=1):
                tempCpnDate = tempCpnDate + timedelta(days=1) # add days till we get to last day of coupon month 
        return tempCpnDate
   
    def nextCpn(self,startDate):
        # 1st guess for next coupon date is maturity date
        tempCpnDate=self.matDate
        flagEndOfMonth=None # Use this to ID a matDate that is the last day of the month
                            # We need this to make sure nextCpn returns a date that is the last day
                            # of the month returned
        if (self.matDate+timedelta(days=1)).day==1:
            flagEndOfMonth=1
        while tempCpnDate-startDate > timedelta(days=0):
            tempCpnDate=tempCpnDate-relativedelta(months=6)
        tempCpnDate=tempCpnDate+relativedelta(months=6)
        if flagEndOfMonth:
            # get 1st day of next month after coupon payment
            day1OfNextMo=tempCpnDate+relativedelta(months=1)
            day1OfNextMo=date(day1OfNextMo.year,day1OfNextMo.month,1)
            while day1OfNextMo - tempCpnDate > timedelta(days=1):
                tempCpnDate = tempCpnDate + timedelta(days=1) # add days till we get to last day of coupon month 
        return tempCpnDate

    def bai(self,cpn,mat,stl):
        pCpn=self.prevCpn(stl)
        return self.cpn/2*100*((self.stlDate-pCpn).days/(self.nextCpn(stl)-pCpn).days)
        