#!/usr/bin/env
# written by Danny Wagstaff 9/2017
from bond import bond
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from math import exp

class UST(bond):
    def __init__(self, matDate, stlDate, cpn, cpnFreq):
        # We will start by only looking at US Treasuries with coupon payments
        #(no zero-coupon bonds)
        self.matDate = matDate
        self.stlDate = stlDate
        self.stlDate = self._getWeekday()
        self.cpn = cpn
        self.cpnFreq = cpnFreq

    def numCoupons(self, basis = 'A/A'):
        # Day count basis = actual/actual. I will add other day count options later
        cpnIndex = 0
        tempDate = self.nextCpn(self.stlDate)
        while tempDate <= self.matDate:
            cpnIndex += 1
            tempDate = self.nextCpn(tempDate)
        return cpnIndex

    def prevCpn(self, startDate):
        # 1st guess for next coupon date is maturity date
        tempCpnDate = self.matDate
        flagEndOfMonth = None ''' Use this to ID a matDate that is the last day
            of the month. We need this to make sure nextCpn returns a date that
            is the last day of the month returned '''
        if (self.matDate + timedelta(days = 1)).day == 1:
            flagEndOfMonth = 1
        while tempCpnDate - startDate > timedelta(days = 0):
            tempCpnDate = tempCpnDate - relativedelta(months = 6)
        if flagEndOfMonth:
            # get 1st day of next month after coupon payment
            day1OfNextMo = tempCpnDate+relativedelta(months = 1)
            day1OfNextMo = date(day1OfNextMo.year, day1OfNextMo.month, 1)
            while day1OfNextMo - tempCpnDate > timedelta(days = 1):
                tempCpnDate = tempCpnDate + timedelta(days = 1) # add days till
                    # we get to last day of coupon month
        return tempCpnDate

    def nextCpn(self, startDate):
        # 1st guess for next coupon date is maturity date
        tempCpnDate = self.matDate
        flagEndOfMonth = None ''' Use this to ID a matDate that is the last day of the month
            We need this to make sure nextCpn returns a date that is the last
            day of the month returned '''
        if (self.matDate + timedelta(days = 1)).day == 1:
            flagEndOfMonth = 1
        while tempCpnDate - startDate > timedelta(days = 0):
            tempCpnDate = tempCpnDate - relativedelta(months = 6)
        tempCpnDate = tempCpnDate+relativedelta(months = 6)
        if flagEndOfMonth:
            # get 1st day of next month after coupon payment
            day1OfNextMo = tempCpnDate + relativedelta(months = 1)
            day1OfNextMo = date(day1OfNextMo.year, day1OfNextMo.month, 1)
            while day1OfNextMo - tempCpnDate > timedelta(days = 1):
                # add days till we get to last day of coupon month
                tempCpnDate = tempCpnDate + timedelta(days = 1)
        return tempCpnDate

    def bai(self, cpn, mat, stl):
        pCpn = self.prevCpn(stl)
        return self.cpn / 2 * 100 * ((self.stlDate - pCpn).days / \
            (self.nextCpn(stl) - pCpn).days)


class UST_Future():
    def __init__(self, ctd, exp_date, first_dlv_date, bond_len = 1):
        self.exp_date = exp_date
        self.ctd = ctd
        self.first_dlv_date = first_dlv_date
        self.bond_len = bond_len
        self.CF = self.getCF(self.first_dlv_date, self.bond_len)

    def _getNextDay1DlvMo(self):
        stlDate = self.stlDate
        if stlDate.month < 3:
            return date(stlDate.year(), 3, 1)
        elif stlDate.month >= 3 and stlDate.month < 6:
            return date(stlDate.year, 6, 1)
        elif stlDate.month >= 6 and stlDate.month < 9:
            return date(stlDate.year, 9, 1)
        elif stlDate.month >= 9 and stlDate.month < 12:
            return date(stlDate.year, 12, 1)
        else: return date(stlDate.year+1, 3, 1)

    def getCF(self, first_dlv_date, bond_len):
        '''
        Calculates the conversion factor for a bond. The CF is the approximate decimal price
        a bond with $1 par value would trade at if it yielded 6% at the start of a particular
        Treasury futures delivery month.
        CF = a * [coupon / 2 + c + d] - b (see CMEGroup.com for more info)
        bond_len = 1 for TU, FV contracts
        bond_len = 2 for TY, TN, US, and UB contracts
        '''
        if first_dlv_date is None:
            day1DlvMo=self._getNextDay1DlvMo()
        else: day1DlvMo = first_dlv_date
        n = relativedelta(self.ctd.matDate, day1DlvMo).years # whole years rounded down
        z = relativedelta(self.ctd.matDate, day1DlvMo).months # whole months rounded down
        if self.bond_len == 2:
            z = int(z / 3) * 3 # this rounds months down to nearest quarter (0,1,2->0, 3,4,5->3, 6,7,8->6,9,10,11->9
        if z < 7:
            v = z
            c = 1 / 1.03 ** (2 * n)
        else:
            if self.bond_len == 2:
                v = 3
            else:
                v = z - 6
            c = 1 / 1.03 ** (2 * n + 1)
        a = 1 / 1.03 ** (v / 6)
        b = self.ctd.cpn / 2 * ((6 - v) / 6)
        d = self.ctd.cpn / 0.06 * (1 - c)
        return round((a * (self.ctd.cpn / 2 + c + d) - b),4)


    def bprFromDFCurve(self, crv, stl = date.today() - timedelta(days = 1)):
        '''
        Takes a discount factor curve and calculates a (synthetic) bond price from it
        crv=discount factor curve
        stl=settlement date
        '''
        arrayDate = list()
        arrayTW = list()
        arrayCpnDates = list()
        while len(crv) > 1:
            substrLen = crv.find(',')
            arrayDate.append(crv[:substrLen])
            crv = crv[-(len(crv) - substrLen - 1):]
            substrLen = crv.find(':')
            arrayTW.append(crv[:(substrLen)])
            crv = crv[-(len(crv) - substrLen):]
            crv = crv[-(len(crv) - 1):]
        numCpns = UST.numCoupons(self.ctd)
        tempDate = stl
        for i in range(numCpns):
            arrayCpnDates.append(self.ctd.nextCpn(tempDate))
            tempDate = arrayCpnDates[i] + timedelta(days = 1)
        invPrice = 0.0
        pvPmt = 0.0
        for j in range(len(arrayCpnDates)):
            tempDate = arrayCpnDates[j]
            for i in range(len(arrayDate) - 1):
                date1 = date(int(arrayDate[i][:4]), int(arrayDate[i][5:7]), int(arrayDate[i][8:10]))
                date2=date(int(arrayDate[i + 1][:4]), int(arrayDate[i + 1][5:7]), int(arrayDate[i + 1][8:10]))
                if (date2 - tempDate).days >= 0 and (date1 - tempDate).days <= 0:
                    pvPmt = self.ctd.cpn / 2 * ((1 / float(arrayTW[i]) * (date2 - tempDate).days +
                    1 / float(arrayTW[i + 1]) * (tempDate - date1).days)) / (date2 - date1).days
                    invPrice = invPrice + pvPmt
                    break
        pvPmt=pvPmt / (self.ctd.cpn / 2)
        invPrice = invPrice + pvPmt
        date1 = date(int(arrayDate[0][:4]), int(arrayDate[0][5:7]), int(arrayDate[0][8:10]))
        date2 = date(int(arrayDate[1][:4]), int(arrayDate[1][5:7]), int(arrayDate[1][8:10]))
        stubRate = 360 * (1 - 1 / float(arrayTW[1])) / (date2 - date1).days
        adjFactor=exp(stubRate * (stl - date1).days / 360)
        bPrice=(100 * invPrice - self.ctd.bai(self.ctd.cpn, self.ctd.matDate, stl)) * adjFactor
        return bPrice


    def dfcurve(self, as_of, stl_date, stub_rate, mat_dates, mat_rates):
        '''creates a discount factor curve string starting from date as_of
           through last date listed in mat_dates. String consists of pairs of
           dates (as strings) and discount factors. The pairs are colon (:) separated
        '''
        crv = str(as_of) + ",1:"
        tw = [None] * 42
        tw[0] = 1 + stub_rate * (stl_date-as_of).days / 360
        tw[1] = (1 + stub_rate * (mat_dates[0] - stl_date).days / 360) * tw[0]
        crv = crv + str(stl_date) + ',' + str(tw[0]) + ':' + str(mat_dates[0]) + ',' + str(tw[1]) + ':'
        for i in self.ctd._incRange(2, len(mat_dates)):
            tw[i] = (1 + (100 - mat_rates[i - 1]) / 100 * (mat_dates[i - 1] - mat_dates[i - 2]).days / 360) * tw[i - 1]
            crv = crv + str(mat_dates[i - 1]) + ',' + str(tw[i]) + ':'
        return crv

    def bimprepo(self, qtdPrice, futPrice, delDate):
        '''
        Returns the implied repo rate (IRR) of the contract. The IRR is the
        rate of return from being long the CTD and short the contract, and
        delivering the CTD into the contract on the optimal day of the delivery
        month.
        '''
        numCpns=self.ctd.numCoupons()
        nextCpn = self.ctd.nextCpn(self.ctd.stlDate)
        invPrice = futPrice * self.CF + self.ctd.bai(self.ctd.cpn, self.ctd.matDate, delDate)
        purPrice = qtdPrice + self.ctd.bai(self.ctd.cpn, self.ctd.matDate, self.ctd.stlDate)
        n = (delDate - self.ctd.stlDate).days
        if numCpns == 0:
            return (invPrice / purPrice - 1) * 360 / n
        elif numCpns == 1:
            t1 = (nextCpn - self.ctd.stlDate).days / 360
            t2 = (delDate - nextCpn).days / 360
            a = purPrice * t1 * t2
            b = purPrice * t1 + purPrice * t2 - self.ctd.cpn / 2 * 100 * t2
            c = purPrice - self.ctd.cpn / 2 * 100 - invPrice
            r1 = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
            r2 = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
            if abs(r1 - self.ctd.cpn / 2 * 100) < abs(r2 - self.ctd.cpn / 2 * 100):
                return r1
            else: return r2
        elif numCpns == 2:
            nextCpn2 = self.ctd.nextCpn(nextCpn + timedelta(days = 1))
            t1 = (nextCpn - self.ctd.stlDate).days / 360
            t2 = (nextCpn2 - nextCpn).days / 360
            t3 = (self.exp_date - nextCpn2).days / 360
            a = purPrice * t1 * t2 * t3
            b = purPrice * t1 * t2 + purPrice * t1 * t3 + purPrice * t2 * t3 - self.ctd.cpn / 2 * 100 * t2 * t3
            c = purPrice * t1 + purPrice * t2 + purPrice * t3 - self.ctd.cpn / 2 * 100 * t2 - self.ctd.cpn * 100 * t3
            d = purPrice - self.ctd.cpn * 100 - invPrice
            # 10 iterations of Newton's Method to approximate implied repo rate, which involves
            # solving a cubic equation
            A_old = self.ctd.cpn
            for i in range(10):
                f_A_old = a * A_old ** 3 + b * A_old ** 2 + c * A_old + d
                df_A_old = 3 * a * A_old ** 2 + 2 * b * A_old + c
                A_new = A_old - f_A_old / df_A_old
                A_old = A_new
            return A_new
        else: return 'Cannot calculate implied repo rate with 3 or more intervening coupons'
