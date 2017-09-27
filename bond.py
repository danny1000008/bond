#!/usr/bin/env
# written by Danny Wagstaff 9/2017
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class bond:
    def __init__(self,cpn,cpnFreq,matDate,stlDate):
        self.cpn=cpn
        self.cpnFreq=cpnFreq
        self.matDate=matDate
        self.stlDate=stlDate
        self.stlDate=self._getWeekday()
        self.convFact=self.getCF()

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
        
    def _incRange(self,start,stop,step=1):
        i=start
        while i <= stop:
            yield i
            i += step

    def getCF(self,dlvDate=None,bondLen=1):
        '''
        Calculates the conversion factor for a bond. The CF is the approximate decimal price
        a bond with $1 par value would trade at if it yielded 6% at the start of a particular
        Treasury futures delivery month.
        CF = a * [coupon / 2 + c + d] - b (see CMEgroup.com for more info)
        bondLen = 1 for TU, FV contracts
        bondLen = 2 for TY, TN, US, and UB contracts
        '''
        if dlvDate is None:
            day1DlvMo=self._getNextDay1DlvMo()
        else: day1DlvMo=dlvDate
        n = relativedelta(self.matDate, day1DlvMo).years # whole years rounded down
        z = relativedelta(self.matDate, day1DlvMo).months # whole months rounded down
        if bondLen==2:
            z = int(z/3)*3 # this rounds months down to nearest quarter (0,1,2->0, 3,4,5->3, 6,7,8->6,9,10,11->9
        if z < 7:
            v = z
            c = 1 / 1.03**(2*n)
        else:
            if bondLen==2:
                v = 3
            else: 
                v = z - 6
            c = 1 / 1.03**(2*n+1)       
        a = 1 / 1.03**(v/6)
        b = self.cpn / 2 * ((6 - v)/6)
        d = self.cpn / 0.06 * (1-c)
        return '%.4f' % round((a * (self.cpn/2+c+d) - b),4)
        
    def bpr2(self,crv,stl=date.today().day-1):
        pass
    
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
        for i in range(2,len(mat_dates) + 1):
            tw[i] = (1 + (100 - mat_rates[i-1])/100 * (mat_dates[i-2] - mat_dates[i-1]).days/360) * tw[i-1]
            crv=crv + str(mat_dates[i-1]) + ',' + str(tw[i]) + ':'
        return crv

    def _getWeekday(self):
        '''
        Checks if a date is on a weekend. If it is, it returns the previous weekday; otherwise
        it returns the original date
        '''
        months={1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
        if self.stlDate.weekday()==5: # 5 = Saturday
            print('Changed settle date from Saturday {0} {1}, {2} to Friday {3} {4}, {5}'
                .format(months[self.stlDate.month],self.stlDate.day,self.stlDate.year,
                months[(self.stlDate-timedelta(1)).month],(self.stlDate-timedelta(1)).day,
                (self.stlDate-timedelta(1)).year))
            self.stlDate=self.stlDate-timedelta(1)
        elif self.stlDate.weekday()==6: # 6 = Sunday
            print('Changed settle date from Sunday {0} {1}, {2} to Friday {3} {4}, {5}'
                .format(months[self.stlDate.month],self.stlDate.day,self.stlDate.year,
                months[(self.stlDate-timedelta(2)).month],(self.stlDate-timedelta(2)).day,
                (self.stlDate-timedelta(2)).year))
            self.stlDate=self.stlDate-timedelta(2)
        return self.stlDate

    def byld(self,price):
        basis='A/A'
        numCpns=self.numCoupons(basis)
        nextCpnDate=self.nextCpn(self.stlDate)
        daysBetwCpns=(nextCpnDate-self.prevCpn(self.stlDate)).days
        daysStlToCpn=(nextCpnDate-self.stlDate).days
        yearFrac=daysStlToCpn/daysBetwCpns
        # initial guess for yield
        r_new = self.cpn
        P_new=price
        P_init=price
        # do 10 iterations of Newton's Method to approximate yield to maturity
        for i in range(10):
            r_old=r_new
            P_old=P_new
            P_new=0
            dP_new=0
            for j in self._incRange(1,numCpns):
                P_new=P_new + (1+r_old/2)**(1-j-yearFrac)
                dP_new=dP_new+(1-j-yearFrac) / 2 * (1+r_old/2)**(-j-yearFrac)
            P_new=P_new*50*self.cpn # same as 100 * cpn / 2    
            P_new=P_new+100*(1+r_old/2)**(1-numCpns-yearFrac)
            P_new=P_new-self.bai(self.cpn,self.matDate,self.stlDate)
            delta_F=P_new-P_init
            dP_new=dP_new*50*self.cpn # same as 100 * cpn / 2
            dP_new=dP_new+50*(1-numCpns-yearFrac)*(1+r_old/2)**(-numCpns-yearFrac)
            r_new=r_old-delta_F/dP_new
        return r_new
    
    def bprice(self,yld):
        tempPrice=0.0
        cpnDate=self.prevCpn(self.stlDate)
        DF_Time=(cpnDate-self.stlDate).days
        while cpnDate<self.matDate:
            cpnDate = self.nextCpn(cpnDate)
            AI_Time = (self.matDate - cpnDate).days
            DF_Time=(cpnDate-self.stlDate).days
            PV_Cpn=self.cpn/self.cpnFreq*100/(1+yld/self.cpnFreq)**(self.cpnFreq*DF_Time/365)
            tempPrice=tempPrice+PV_Cpn
        PV_Par=100/(1+yld/self.cpnFreq)**(self.cpnFreq*DF_Time/365)
        tempPrice = tempPrice + PV_Par-self.bai(self.cpn, self.matDate, self.stlDate)
        return tempPrice
    
    def dv01(self,yld):
        '''
        The dv01 function calculates how much changing the bond yield by 1 basis point (0.01%) changes
        the bond price. We average the price move for an increase in yield and a decrease in yield in
        order to lessen the impact of the bond's convexity on dv01.
        '''
        bPx=self.bprice(yld)
        bPxBumpUp=self.bprice(yld+0.0001)
        bPxBumpDown=self.bprice(yld-0.0001)
        return (abs(bPx-bPxBumpUp)+abs(bPx-bPxBumpDown))/2
    
    def numCoupons(self, basis):
        cpnIndex=0
        tempDate=self.nextCpn(self.stlDate)
        while tempDate <= self.matDate:
            cpnIndex+=1
            tempDate=self.nextCpn(tempDate)
        return cpnIndex

    def bai(self,cpn,mat,stl):
        pCpn=self.prevCpn(stl)
        return self.cpn/2*100*((self.stlDate-pCpn).days/(self.nextCpn(stl)-pCpn).days)
        
    
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
        
    
    def nextCpn2(self,startDate):
        '''
        # 1st guess for next coupon date is maturity date
        tempCpnDate=date(startDate.year,self.matDate.month,self.matDate.day)
        flagEndOfMonth=None # Use this to ID a matDate that is the last day of the month
                            # We need this to make sure nextCpn returns a date that is the last day
                            # of the month returned
        if (self.matDate+timedelta(days=1)).day==1:
            flagEndOfMonth=1
        while tempCpnDate-startDate < timedelta(days=0):
            tempCpnDate=tempCpnDate+relativedelta(months=6)
        if flagEndOfMonth:
            # get 1st day of next month after coupon payment
            day1OfNextMo=tempCpnDate+relativedelta(months=1)
            day1OfNextMo=date(day1OfNextMo.year,day1OfNextMo.month,1)
            while day1OfNextMo - tempCpnDate > timedelta(days=1):
                tempCpnDate = tempCpnDate + timedelta(days=1) # add days till we get to last day of coupon month 
        return tempCpnDate
        '''
    
def main():
    stlDate=date(2017,10,4)
    #stlDate=date.today()-timedelta(1)
    b1=bond(0.01625,2,date(2019,6,30),stlDate)
    b2=bond(0.0175,2,date(2021,11,30),stlDate)
    b3=bond(0.025,2,date(2024,5,15),stlDate)
    b4=bond(0.0175,2,date(2019,9,30),stlDate)
    b5=bond(0.01875,2,date(2022,2,28),stlDate)
    b6=bond(0.02375,2,date(2024,8,15),stlDate)
    b7=bond(0.0225,2,date(2027,2,15),stlDate)
    b8=bond(0.02375,2,date(2027,5,15),stlDate)
    matDates=(date(2017,12,18),date(2018,3,18),date(2018,6,19),date(2018,9,18))
    matRates=(98.685,98.6,98.54,98.49)
    print(b1.dfcurve(date(2017,9,11), date(2017,9,12), 0.012, matDates, matRates))
    print('b1 previous coupon date',b1.prevCpn(stlDate))
    print('b1 next coupon date',b1.nextCpn(stlDate))
    print('b1 number of coupons remaining:',b1.numCoupons('A/A'))
    print('b1 CF',b1.getCF(date(2017,9,1), 1))
    print('b1 ai',b1.bai(b1.cpn, b1.matDate, b1.stlDate))
    print('b1 yield',b1.byld(100))
    print('b1 price',b1.bprice(0.01625))
    print('b1 DV01',b1.dv01(0.01424)*10000)
    print('b2 previous coupon date',b2.prevCpn(stlDate))
    print('b2 next coupon date',b2.nextCpn(stlDate))
    print('b2 number of coupons remaining:',b2.numCoupons('A/A'))
    print('b2 CF',b2.getCF(date(2017,9,1), 1))
    print('b2 ai',b2.bai(b2.cpn, b2.matDate, b2.stlDate))
    print('b2 yield',b2.byld(100))
    print('b3 previous coupon date',b3.prevCpn(stlDate))
    print('b3 next coupon date',b3.nextCpn(stlDate))
    print('b3 number of coupons remaining:',b3.numCoupons('A/A'))
    print('b3 CF',b3.getCF(date(2017,9,1), 2))
    print('b3 yield',b3.byld(100))
    print('b4 previous coupon date',b4.prevCpn(stlDate))
    print('b4 next coupon date',b4.nextCpn(stlDate))
    print('b4 number of coupons remaining:',b4.numCoupons('A/A'))
    print('b4 CF',b4.getCF(date(2017,12,1), 1))
    print('b4 yield',b4.byld(100))
    print('b5 previous coupon date',b5.prevCpn(stlDate))
    print('b5 next coupon date',b5.nextCpn(stlDate))
    print('b5 number of coupons remaining:',b5.numCoupons('A/A'))
    print('b5 CF',b5.getCF(date(2017,12,1), 1))
    print('b5 yield',b5.byld(100))
    print('b6 previous coupon date',b6.prevCpn(stlDate))
    print('b6 next coupon date',b6.nextCpn(stlDate))
    print('b6 number of coupons remaining:',b6.numCoupons('A/A'))
    print('b6 CF',b6.getCF(date(2017,12,1), 2))
    print('b6 yield',b6.byld(100))
    print('b7 CF',b7.getCF(date(2017,9,1), 2))
    print('b7 yield',b7.byld(100))
    print('b8 CF',b8.getCF(date(2017,12,1), 2))
    print('b8 yield',b8.byld(100))
    
if __name__=="__main__":
    main()