#!/usr/bin/env
# written by Danny Wagstaff 9/2017
from bond import bond
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from math import exp

class UST(bond):
    def __init__(self,matDate,stlDate,cpn,cpnFreq):
        self.matDate=matDate
        self.stlDate=stlDate
        self.stlDate=self._getWeekday()
        self.cpn=cpn
        self.cpnFreq=cpnFreq
        
    def numCoupons(self, basis='A/A'):
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
        
class UST_Future():
    def __init__(self,CTD,expDate,firstDlvDate,bondLen=1):
        self.CTD=CTD
        self.expDate=expDate
        self.firstDlvDate=firstDlvDate
        self.bondLen=bondLen
        self.CF=self.getCF(self.firstDlvDate, self.bondLen)
        
    def _getNextDay1DlvMo(self):
        stlDate=self.stlDate
        if stlDate.month < 3:
            return date(stlDate.year(),3,1)
        elif stlDate.month >= 3 and stlDate.month < 6:
            return date(stlDate.year,6,1)
        elif stlDate.month >= 6 and stlDate.month < 9:
            return date(stlDate.year,9,1)
        elif stlDate.month >= 9 and stlDate.month < 12:
            return date(stlDate.year,12,1)
        else: return date(stlDate.year+1,3,1)
        
    def getCF(self,firstDlvDate,bondLen):
        '''
        Calculates the conversion factor for a bond. The CF is the approximate decimal price
        a bond with $1 par value would trade at if it yielded 6% at the start of a particular
        Treasury futures delivery month.
        CF = a * [coupon / 2 + c + d] - b (see CMEGroup.com for more info)
        bondLen = 1 for TU, FV contracts
        bondLen = 2 for TY, TN, US, and UB contracts
        '''
        if firstDlvDate is None:
            day1DlvMo=self._getNextDay1DlvMo()
        else: day1DlvMo=firstDlvDate
        n = relativedelta(self.CTD.matDate, day1DlvMo).years # whole years rounded down
        z = relativedelta(self.CTD.matDate, day1DlvMo).months # whole months rounded down
        if self.bondLen==2:
            z = int(z/3)*3 # this rounds months down to nearest quarter (0,1,2->0, 3,4,5->3, 6,7,8->6,9,10,11->9
        if z < 7:
            v = z
            c = 1 / 1.03**(2*n)
        else:
            if self.bondLen==2:
                v = 3
            else: 
                v = z - 6
            c = 1 / 1.03**(2*n+1)       
        a = 1 / 1.03**(v/6)
        b = self.CTD.cpn / 2 * ((6 - v)/6)
        d = self.CTD.cpn / 0.06 * (1-c)
        return '%.4f' % round((a * (self.CTD.cpn/2+c+d) - b),4)
    
    def bpr2(self,crv,stl=date.today()-timedelta(days=1)):
        '''
        Takes a discount factor curve and calculates a (synthetic) bond price from it
        crv=discount factor curve
        stl=settlement date
        '''
        arrayDate=list()
        arrayTW=list()
        arrayCpnDates=list()
        while len(crv)>1:
            substrLen=crv.find(',')
            arrayDate.append(crv[:substrLen])
            print('arrayDate',arrayDate)
            crv=crv[-(len(crv)-substrLen-1):]
            print('crv',crv)
            substrLen=crv.find(':')
            arrayTW.append(crv[:(substrLen)])
            print('arrayTW',arrayTW)
            crv=crv[-(len(crv)-substrLen):]
            print('crv',crv)
            crv=crv[-(len(crv)-1):]
            print('crv',crv)
        numCpns=UST.numCoupons(self.CTD)
        print('numCpns',numCpns)
        tempDate=stl
        for i in range(numCpns):
            arrayCpnDates.append(self.CTD.nextCpn(tempDate))
            tempDate=arrayCpnDates[i]+timedelta(days=1)
            print('arrayCpnDates',arrayCpnDates)
        invPrice=0.0
        pvPmt=0.0
        for j in range(len(arrayCpnDates)):
            tempDate=arrayCpnDates[j]
            print('arrayDate',arrayDate[i+1],'tempDate',tempDate)
            for i in range(len(arrayDate)-1):
                date1=date(int(arrayDate[i][:4]),int(arrayDate[i][5:7]),int(arrayDate[i][8:10]))
                date2=date(int(arrayDate[i+1][:4]),int(arrayDate[i+1][5:7]),int(arrayDate[i+1][8:10]))
                print('i',i,'date1',date1,',date2',date2)
                if (date2-tempDate).days>=0 and (date1-tempDate).days<=0:
                    pvPmt=self.CTD.cpn/2*((1/float(arrayTW[i])*(date2-tempDate).days +
                    1/float(arrayTW[i+1])*(tempDate-date1).days)) / (date2-date1).days
                    invPrice=invPrice+pvPmt
                    break
        pvPmt=pvPmt/(self.CTD.cpn/2)
        invPrice=invPrice+pvPmt
        date1=date(int(arrayDate[1][:4]),int(arrayDate[1][5:7]),int(arrayDate[1][8:10]))
        date2=date(int(arrayDate[2][:4]),int(arrayDate[2][5:7]),int(arrayDate[2][8:10]))
        stubRate=360*(1-1/float(arrayTW[2])) / (date2-date1).days
        adjFactor=exp(stubRate*(stl-date1).days/360)
        bpr2=(100*invPrice-self.CTD.bai(self.CTD.cpn,self.CTD.matDate,stl))*adjFactor
        return bpr2
                       
    
    def dfcurve(self,as_of,stl_date, stub_rate,mat_dates, mat_rates):
        '''creates a discount factor curve string starting from date as_of 
           through last date listed in mat_dates. String consists of pairs of
           dates (as strings) and discount factors. The pairs are colon (:) separated
        '''
        crv=str(as_of) + ",1:"
        tw=[None] * 40
        tw[0]=1 + stub_rate * (as_of - stl_date).days/360
        tw[1]=1 + stub_rate * (stl_date - mat_dates[0]).days/360
        crv=crv + str(stl_date) + ',' + str(tw[0]) + ':' + str(mat_dates[0]) + ',' + str(tw[1]) + ':'
        for i in self.CTD._incRange(2,len(mat_dates)):
            tw[i] = (1 + (100 - mat_rates[i-1])/100 * (mat_dates[i-2] - mat_dates[i-1]).days/360) * tw[i-1]
            crv=crv + str(mat_dates[i-1]) + ',' + str(tw[i]) + ':'
        return crv