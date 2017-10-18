#!/usr/bin/env
# written by Danny Wagstaff 9/2017
from datetime import date, timedelta

class bond:
    def __init__(self,matDate,stlDate,cpn=None,cpnFreq=None):
        #def __init__(self,cpn,cpnFreq,matDate,stlDate):
        self.matDate=matDate
        self.stlDate=stlDate
        self.stlDate=self._getWeekday()
        self.cpn=cpn
        self.cpnFreq=cpnFreq

        
    def _incRange(self,start,stop,step=1):
        i=start
        while i <= stop:
            yield i
            i += step


    def _getWeekday(self):
        '''
        Checks if a date is on a weekend. If it is, it returns the previous weekday; otherwise
        it returns the original date
        '''
        months={1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
        if self.stlDate.isoweekday()==6: # 6 = Saturday
            print('Changed settle date from Saturday {0} {1}, {2} to Friday {3} {4}, {5}'
                .format(months[self.stlDate.month],self.stlDate.day,self.stlDate.year,
                months[(self.stlDate-timedelta(1)).month],(self.stlDate-timedelta(1)).day,
                (self.stlDate-timedelta(1)).year))
            self.stlDate=self.stlDate-timedelta(1)
        elif self.stlDate.isoweekday()==7: # 7 = Sunday
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
        while cpnDate<self.matDate:
            cpnDate = self.nextCpn(cpnDate)
            DF_Time=(cpnDate-self.stlDate).days
            PV_Cpn=self.cpn/self.cpnFreq*100/((1+yld/self.cpnFreq)**(self.cpnFreq*DF_Time/365))
            tempPrice=tempPrice+PV_Cpn
        PV_Par=100/((1+yld/self.cpnFreq)**(self.cpnFreq*DF_Time/365))
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
    
    
def main():
    stlDate=date(2017,10,4)
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