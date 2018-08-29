#!/usr/bin/env
# written by Danny Wagstaff 9/2017
from datetime import date, timedelta

class Bond:
    def __init__(self, maturity_date, settle_date, coupon = None, coupon_frequency = 2):
        self.maturity_date = maturity_date
        self.settle_date = settle_date
        self.settle_date = self._get_weekday()
        self.coupon = coupon
        self.coupon_frequency = coupon_frequency


    def _inc_range(self, start, stop, step = 1):
        # an iterator function that iterates from start to stop, inclusive
        i = start
        while i <= stop:
            yield i
            i += step


    def _get_weekday(self):
        '''
        Checks if a date is on a weekend. If it is, it returns the previous weekday; otherwise
        it returns the original date
        '''
        months={1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May',
            6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October',
            11: 'November', 12: 'December'}
        if self.settle_date.isoweekday() == 6: # 6 = Saturday
            print('Changed settle date from Saturday {0} {1}, {2} to Friday {3} {4}, {5}'
                .format(months[self.settle_date.month],self.settle_date.day,self.settle_date.year,
                months[(self.settle_date-timedelta(1)).month],(self.settle_date-timedelta(1)).day,
                (self.settle_date-timedelta(1)).year))
            self.settle_date = self.settle_date - timedelta(1)
        elif self.settle_date.isoweekday() == 7: # 7 = Sunday
            print('Changed settle date from Sunday {0} {1}, {2} to Friday {3} {4}, {5}'
                .format(months[self.settle_date.month],self.settle_date.day,self.settle_date.year,
                months[(self.settle_date-timedelta(2)).month],(self.settle_date-timedelta(2)).day,
                (self.settle_date-timedelta(2)).year))
            self.settle_date = self.settle_date - timedelta(2)
        return self.settle_date

    def bond_price(self, bond_yield):
        ''' Calculates the price of a bond from its yield to maturity
        '''
        temp_price = 0.0
        coupon_date = self.previous_coupon(self.settle_date)
        while coupon_date < self.maturity_date:
            coupon_date = self.next_coupon(coupon_date)
            discount_factor_time = (coupon_date - self.settle_date).days
            present_value_coupon = self.coupon / self.coupon_frequency * 100 / ((1 + bond_yield / self.coupon_frequency)**
                (self.coupon_frequency * discount_factor_time / 365))
            temp_price = temp_price + present_value_coupon
        present_value_par = 100 / ((1 + bond_yield / self.coupon_frequency) ** (self.coupon_frequency * discount_factor_time / 365))
        temp_price = temp_price + present_value_par-self.accrued_interest(self.coupon, self.maturity_date, self.settle_date)
        return temp_price

    def dv01(self, bond_yield):
        '''
        The dv01 function calculates how much changing the bond yield by 1 basis point (0.01%) changes
        the bond price. We average the price move for an increase in yield and a decrease in yield in
        order to lessen the impact of the bond's convexity on dv01.
        '''
        bond_price = self.bond_price(bond_yield)
        bond_price_bump_up = self.bond_price(bond_yield + 0.0001)
        bond_price_bump_down = self.bond_price(bond_yield - 0.0001)
        return (abs(bond_price - bond_price_bump_up) + abs(bond_price - bond_price_bump_down)) / 2

    def next_coupon(self, settle_date):
        '''
        Returns date of next coupon payment after settle_date
        '''
        new_date = date(self.maturity_date.year, self.maturity_date.month, self.maturity_date.day)
        #cpnNPlus1 = new_date;
        while new_date > settle_date:
            new_date -= timedelta(days = 185)
            new_date = date(new_date.year, new_date.month, self._get_coupon_day_of_month(new_date.month))
        new_date += timedelta(days = 180)
        new_date = date(new_date.year, new_date.month, self._get_coupon_day_of_month(new_date.month))
        return new_date

    def previous_coupon(self, settle_date):
        '''
        Returns date of previous coupon payment before settle_date
        '''
        bond_coupon_next = self.next_coupon(settle_date)
        coupon_previous = date(bond_coupon_next.year - 1, bond_coupon_next.month, bond_coupon_next.day)
        return self.next_coupon(coupon_previous)
        def get_number_of_coupons(self, settle_date = self.settle_date, basis = 'A/A'):
            '''
            Returns number of coupons remaining after settle_date
            '''

        count = 0
        bond_coupon_next = self.next_coupon(settle_date)
        while bond_coupon_next < self.maturity_date:
            count += 1
            bond_coupon_next = self.next_coupon(bond_coupon_next + timedelta(1))
        #print('count=', count + 1)
        return count + 1

    def _get_coupon_day_of_month(self, month):
        '''
        Returns the day of the month that a coupon payment will be made
        (typically the 15th or the last day of the month)
        '''
        days_in_month = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31,
            9: 30, 10: 31, 11: 30, 12: 31}
        guess1 = days_in_month[month]
        if self.maturity_date.day < 28:
            guess1 = self.maturity_date.day
        return guess1

    def accrued_interest(self):
        '''
        Returns the accrued interest from the last coupon payment till self.settle_date
        '''
        date_of_prev_coupon = self.previous_coupon(self.settle_date)
        days_in_period = (self.next_coupon(self.settle_date) - date_of_prev_coupon).days
        days_of_interest = (self.settle_date - date_of_prev_coupon).days
        interest = self.coupon / self.coupon_frequency * (days_of_interest / (1.0 * days_in_period)) * 100
        return interest

    def bond_yield(self, price):
        '''
        Returns the yield to maturity of the bond, given a price
        '''
        basis = 'A/A' # actual/actual day count. In the future I will add other day count options
        number_of_coupons = self.get_number_of_coupons(basis)
        prev_coupon_date = self.previous_coupon(self.settle_date)
        next_coupon_date = self.next_coupon(self.settle_date)
        days_between_coupons = (next_coupon_date - prev_coupon_date).days
        settle_date_to_coupon_date = (next_coupon_date - self.settle_date).days
        year_fraction = settle_date_to_coupon_date / (1.0 * days_between_coupons)
        # initial guess for yield
        r_new = self.coupon
        P_new = price
        P_init = price
        # do 10 iterations of Newton's Method to approximate yield to maturity
        interest = self.accrued_interest()
        for i in range(10):
            r_old = r_new
            P_old = P_new
            P_new = 0
            dP_new = 0
            for j in self._inc_range(1, number_of_coupons):
                P_new = P_new + (1 + r_old / 2.0) ** (1 - j - year_fraction)
                dP_new = dP_new + (1 - j - year_fraction) / 2.0 * (1 + r_old / 2.0) ** \
                    (-j - year_fraction)
            P_new = P_new * 100 * self.coupon / self.coupon_frequency
            P_new = P_new + 100 * (1 + r_old / 2.0) ** (1 - number_of_coupons - year_fraction)
            P_new = P_new - interest
            delta_F = P_new - P_init
            dP_new = dP_new * 100 * self.coupon / self.coupon_frequency
            dP_new = dP_new + 50 * (1 - number_of_coupons - year_fraction) * (1 + r_old / 2.0) ** \
                (-number_of_coupons - year_fraction)
            r_new = r_old - delta_F / dP_new
        return round(r_new * 100, 3)
