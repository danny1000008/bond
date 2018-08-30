# bond.py
Defines classes for generic fixed-income bonds, US Treasury bonds, and US Treasury futures.

## Getting Started
  1. Create a directory to download repository into.
  2. Download the repo (git clone https://github.com/danny1000008/bond.git)
  3. Set up a Python 3.x virtual environment.
  4. Install dependencies: `pip install -r requirements.txt`
  5. Run the program: `python main.py` This starts the Flask web server.
  6. Open a web browser and go to [localhost:5000](localhost:5000).

## Prerequisites
  1. Python 3.x
  2. Packages from requirements.txt, either installed globally or in a virtual environment.

## Bond, US Treasury, and US Treasury futures classes

## How to install dependencies
pip install -r requirements.txt

## How to run the program
python main.py

## How to run tests
no tests yet

## Classes, properties, methods

### 1. Bond - class that defines a coupon-paying, fixed-income bond, with
      A. Properties
        1. maturity_date - date; the date that the bond matures (expires).
        2. coupon - float; decimal value of coupon (ex: a 2% coupon would be 0.02)
        3. coupon_frequency - int; number of coupons per year.
        4. settle_date - date; the settlement date (used to calculate bond price,
           yield, etc.)
      B. Methods
        1. bond_price(bond_yield) - returns price of bond for a given (decimal)
           yield
        2. dv01(bond_yield) - returns the $ amount that the bond price changes for
           a 1 basis point (0.01%) change in its' yield.
        3. previous_coupon(settle_date) - returns the date of the first coupon
           payment before the given settlement date.
        4. next_coupon(settle_date) - returns the date of the first coupon payment
           after the given settlement date.
        5. accrued_interest() - returns the accrued interest from the last coupon
           payment till self.settle_date.
        6. bond_yield(bond_price) - returns the bond's yield to maturity, given its'
           price.
        7. get_number_of_coupons(settle_date = self.settle_date, basis = 'A/A') -
           returns number of coupons remaining after settle_date.

### 2. UST - inherits from Bond. Class for US Treasuries. Not finished!!

### 3. UST_Future - class that provides methods for US Treasury futures contracts.
   ### Also not finished!
      A. Properties
        1. ctd - class UST; US Treasury security that is "cheapest-to-deliver" into
           contract
        2. expDate - expiration date of contract
        3. first_dlv_date - first day that an eligible US Treasury security can be
           delivered into contract.
        4. bond_len - bond_len = 1 for TU (2 year), FV (5 year) contracts
           bond_len = 2 for TY (10 year), TN (Ultra 10 year), US (bond), and
           UB (Ultra bond) contracts. Used in calculating conversion factor (CF) for
           contract.
        5. CF - conversion factor for contract.
      B. Methods
        1. getCF(first_dlv_date, bond_len) - returns the conversion factor for a
           bond.
        2. bprFromDFCurve(crv, stl = date.today() - timedelta(days = 1)) - Takes a
           discount factor (df) curve and returns a (synthetic) bond price from it.
        3. dfcurve(as_of, stl_date, stub_rate, mat_dates, mat_rates) - creates a
           discount factor curve string starting from date as_of through last date
           listed in mat_dates.
        4. bimprepo(qtdPrice, futPrice, delDate) - returns the implied repo rate of
           a contract.

## Motivation
  1. I wanted to build a project to develop my skills as a software developer, particularly in Python.
  2. I noticed that there wasn't any way to see the "basket" of US Treasury securities that are deliverable into a US Treasury futures contract, outside of a Bloomberg terminal, or other high-priced market data applications.
