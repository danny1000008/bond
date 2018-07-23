import unittest
import bond
from datetime import date

class test_bond_methods(unittest.TestCase):
    def test_yield5(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,6,15)
        b1=bond.bond(expiration_date, settle_date, 0.015, 2)
        self.assertEqual(round(b1.bond_yield(98), 3), 2.566)

    def test_yield1(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,6,30)
        b1=bond.bond(expiration_date, settle_date, 0.025, 2)
        self.assertEqual(round(b1.bond_yield(99.875), 3), 2.565)


    def test_yield9(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,6,30)
        b1=bond.bond(expiration_date, settle_date, 0.01625, 2)
        self.assertEqual(round(b1.bond_yield(98.188), 3), 2.571)

    def test_yield4(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,7,15)
        b1=bond.bond(expiration_date, settle_date, 0.015, 2)
        self.assertEqual(round(b1.bond_yield(97.906), 3), 2.572)

    def test_yield8(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,7,31)
        b1=bond.bond(expiration_date, settle_date, 0.01625, 2)
        self.assertEqual(round(b1.bond_yield(98.094), 3), 2.58)

    def test_yield3(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,8,15)
        b1=bond.bond(expiration_date, settle_date, 0.015, 2)
        self.assertEqual(round(b1.bond_yield(97.812), 3), 2.576)

    def test_yield7(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,8,31)
        b1=bond.bond(expiration_date, settle_date, 0.01375, 2)
        self.assertEqual(round(b1.bond_yield(97.469), 3), 2.596)

    def test_yield2(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,9,15)
        b2=bond.bond(expiration_date, settle_date, 0.01375, 2)
        self.assertEqual(round(b2.bond_yield(97.406), 3), 2.604)

    def test_yield6(self):
        settle_date=date(2018,7,9)
        expiration_date = date(2020,9,30)
        b1=bond.bond(expiration_date, settle_date, 0.01375, 2)
        self.assertEqual(round(b1.bond_yield(97.375), 3), 2.595)



def main():
    settle_date=date(2018,7,5)
    b1=bond.bond(date(2020,6,30), settle_date, 0.025, 2)
    return b1.bond_yield()
    '''
    b2=bond(0.0175,2,date(2021,11,30),stlDate)
    b3=bond(0.025,2,date(2024,5,15),stlDate)
    b4=bond(0.0175,2,date(2019,9,30),stlDate)
    b5=bond(0.01875,2,date(2022,2,28),stlDate)
    b6=bond(0.02375,2,date(2024,8,15),stlDate)
    b7=bond(0.0225,2,date(2027,2,15),stlDate)
    b8=bond(0.02375,2,date(2027,5,15),stlDate)
    matDates=(date(2017,12,18),date(2018,3,18),date(2018,6,19),date(2018,9,18))
    matRates=(98.685,98.6,98.54,98.49)
    print(b1.dfcurve(date(2017,9,11), date(2017,9,12), 0.0136, matDates, matRates))
    print('b1 previous coupon date',b1.previous_coupon(stlDate))
    print('b1 next coupon date',b1.next_coupon(stlDate))
    print('b1 number of coupons remaining:',b1.get_number_of_coupons('A/A'))
    print('b1 CF',b1.getCF(date(2017,9,1), 1))
    print('b1 ai',b1.accrued_interest(b1.cpn, b1.matDate, b1.stlDate))
    print('b1 yield',b1.byld(100))
    print('b1 price',b1.bond_price(0.01625))
    print('b1 DV01',b1.dv01(0.01424)*10000)
    print('b2 previous coupon date',b2.previous_coupon(stlDate))
    print('b2 next coupon date',b2.next_coupon(stlDate))
    print('b2 number of coupons remaining:',b2.get_number_of_coupons('A/A'))
    print('b2 CF',b2.getCF(date(2017,9,1), 1))
    print('b2 ai',b2.accrued_interest(b2.cpn, b2.matDate, b2.stlDate))
    print('b2 yield',b2.byld(100))
    print('b3 previous coupon date',b3.previous_coupon(stlDate))
    print('b3 next coupon date',b3.next_coupon(stlDate))
    print('b3 number of coupons remaining:',b3.get_number_of_coupons('A/A'))
    print('b3 CF',b3.getCF(date(2017,9,1), 2))
    print('b3 yield',b3.byld(100))
    print('b4 previous coupon date',b4.previous_coupon(stlDate))
    print('b4 next coupon date',b4.next_coupon(stlDate))
    print('b4 number of coupons remaining:',b4.get_number_of_coupons('A/A'))
    print('b4 CF',b4.getCF(date(2017,12,1), 1))
    print('b4 yield',b4.byld(100))
    print('b5 previous coupon date',b5.previous_coupon(stlDate))
    print('b5 next coupon date',b5.next_coupon(stlDate))
    print('b5 number of coupons remaining:',b5.get_number_of_coupons('A/A'))
    print('b5 CF',b5.getCF(date(2017,12,1), 1))
    print('b5 yield',b5.byld(100))
    print('b6 previous coupon date',b6.previous_coupon(stlDate))
    print('b6 next coupon date',b6.next_coupon(stlDate))
    print('b6 number of coupons remaining:',b6.get_number_of_coupons('A/A'))
    print('b6 CF',b6.getCF(date(2017,12,1), 2))
    print('b6 yield',b6.byld(100))
    print('b7 CF',b7.getCF(date(2017,9,1), 2))
    print('b7 yield',b7.byld(100))
    print('b8 CF',b8.getCF(date(2017,12,1), 2))
    print('b8 yield',b8.byld(100))
    '''
if __name__=="__main__":
    unittest.main()
