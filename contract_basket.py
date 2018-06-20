#!/usr/bin/env
# written by Danny Wagstaff 9/2017

from datetime import date, timedelta
import json  # Can we group all standard library imports at the top?
import os.path
import urllib3
import certifi
import xmltodict
import bond

class Basket(list):
    def __init__(self, name = '', val = list()):
        self.name = name
        self.value = val
        self.stl_date = self.get_latest_stl_date()
        self.fc = '' # futures contract
        self.fe = '' #futures expiration (e.g., Jun 2018)
        self.list_CUSIPs = []
    # There's no need to abbreviate so much if you use an editor that autocompletes

    def get_dlv_dates(self, exp):
        '''
        Returns first and last days of the delivery month (March, June,
        September, or December) for the US Treasury (UST) futures contract
        '''
        exp = exp.split()
        dict_exp = {'Mar': 3, 'Jun': 6, 'Sep': 9, 'Dec': 12}
        day1_del_month = date(int(exp[1]), dict_exp[exp[0]], 1)
        day_last_del_month = 0
        if day1_del_month.month == 12:
            day_last_del_month = date(day1_del_month.year, 12, 31)
        else:
            day_last_del_month = date(day1_del_month.year, day1_del_month.month + 1,
            day1_del_month.day) - timedelta(days = 1)
        return (day1_del_month, day_last_del_month)

        # Docstrings are used for documentation, not commenting. What editor do
        # you use?

        # Have you heard of Maya? It is a library for datetime manipulation.
        # Is there a way to simplify the following logic?

    # Can we think of a better variable name than dt?
    def get_con_abbr(self, con_prefix = '', today = date.today()):
        '''
        Returns a 4 character string: the UST futures contract abbreviation, which consists of the contract (TU, FV, TY, TN, US, OR UB),
        the expiration month (H = March, M = June, U = September, Z = December), and the last digit of the expiration year
        '''
        dict_exp = {'Mar': 'H', 'Jun': 'M', 'Sep': 'U', 'Dec': 'Z'}
        exp = today.split()
        return ''.join([con_prefix, dict_exp[exp[0]], str(exp[1][3])])

    def get_mat_date(self, ust_sec):
        '''
        Returns the maturity date of a UST security in yyyy-mm-dd form
        '''
        # What can we about the unnecessary repetition?
        # Have you tried using regular expressions yet?
        return date(int(ust_sec["maturityDate"][0:4]), int(ust_sec["maturityDate"][5:7]), int(ust_sec["maturityDate"][8:10]))

    def get_web_pg(self, sec = "Note"):
        '''
        Uses urllib3 to get and return a list of UST securities (either notes or bonds) from treasurydirect.gov's API
        '''
        # Have you used the requests library? It is a higher level library than
        # urllib3.
        # Consider using string concatenation to create the URL string.
        # Consider returning a string instead of bytes.
        url_obj = urllib3.PoolManager(cert_reqs = "CERT_REQUIRED", ca_certs = certifi.where())
        return url_obj.request("GET", ''.join(["https://www.treasurydirect.gov/TA_WS/securities/search?format=json&type=", sec]))

    def get_specs(self, fc):
        '''
        Returns 1) the minimum time between the first day of the delivery month and the UST security's maturity date, and
                2) the maximum time between the last day of the delivery month and the UST security's maturity date
        The specifications for each UST futures contract are listed below for reference (copied from
        http://www.cmegroup.com/trading/interest-rates/#uSTreasuries)

        TU Contract Delivery Specifications
        U.S. Treasury notes with an original term to maturity of
        1) not more than five years and three months and a remaining term to maturity of
        2) not less than one year and nine months from the first day of the delivery month and a remaining
        term to maturity of
        3) not more than two years from the last day of the delivery month.

        FV Contract Delivery Specifications
        U.S. Treasury notes with an original term to maturity of
        1) not more than five years and three months and a remaining term to maturity of
        2) not less than 4 years and two months as of the first day of the delivery month.

        TY Contract Delivery Specifications
        U.S. Treasury notes with an remaining term to maturity of
        1) at least 6.5 years as of the first day of the delivery month.
        2) not more than 10 years as of the first day of the delivery month.

        TN Contract Delivery Specifications
        Original issue 10 Year U.S. Treasury notes with an remaining term to maturity of
        1) at least 9.41667 years (9 years, 5 months)  as of the first day of the delivery month.
        2) not more than 10 years as of the first day of the delivery month.

        US Contract Delivery Specifications
        U.S. Treasury notes with an remaining term to maturity of
        1) at least 15 years as of the first day of the delivery month.
        2) not more than 25 years as of the first day of the delivery month.

        UB Contract Delivery Specifications
        U.S. Treasury notes with an remaining term to maturity of
        1) at least 25 years as of the first day of the delivery month.
        '''
        # Can we break up the dict literal into multiple lines to increase readability?
        # Consider using the types in the py-moneyed package to do financial
        # calculations.
        dict_specs = {'TU': {'ttm_min': {'years': 1, 'months': 9}, 'max_to_day_last': {'years': 2, 'months': 0}},
            'FV': {'ttm_min': {'years': 4, 'months': 2}, 'max_to_day_last': {'years': 5, 'months': 3}},
            'TY': {'ttm_min': {'years': 6, 'months': 6}, 'max_to_day_last': {'years': 10, 'months': 0},
            'ttm_max': {'years': 10, 'months': 0}},
            'TN':{'ttm_min': {'years': 9, 'months': 5}, 'max_to_day_last': {'years': 10, 'months': 0},
            'ttm_max': {'years': 10, 'months': 0}},
            'US': {'ttm_min': {'years': 15, 'months': 0}, 'max_to_day_last': {'years': 25, 'months': 0},
            'ttm_max': {'years': 25, 'months': 0}},
            'UB': {'ttm_min': {'years': 25, 'months': 0}, 'max_to_day_last': {'years': 30, 'months': 0},
            'ttm_max': {'years': 30, 'months': 0}}}
        #dict_specs = {'TU': {'ttm_min': 1.75, 'max_to_day_last': 2},
        #'FV': {'ttm_min': 4.1667, 'max_to_day_last': 5.25},
        #'TY': {'ttm_min': 6.5, 'max_to_day_last': 10.0833},
        #'TN': {'ttm_min': 9.4167, 'max_to_day_last': 10.0833},
        #'US': {'ttm_min': 15, 'max_to_day_last': 25.0833},
        #'UB': {'ttm_min': 25, 'max_to_day_last': 30.0833}}
        return dict_specs[fc]


    def get_terms(self, fc):
        '''
        Returns a dictionary of original times to maturity of UST securities eligible to be delivered into the UST futures contract (given by fc)
        '''
        terms = {'TU': {"2-Year": 2, "3-Year": 3, "5-Year": 5},
            'FV': {"5-Year": 5},
            'TY': {"7-Year": 7, "9-Year 10-Month": 9.8333, "9-Year 11-Month": 9.9167, "10-Year": 10},
            'TN': {"9-Year 10-Month": 9.8333, "9-Year 11-Month": 9.9167, "10-Year": 10}, 'US': {"29-Year 10-Month": 29.8333, "29-Year 11-Month": 29.9167,"30-Year": 30},
            'UB': {"29-Year 10-Month": 29.8333, "29-Year 11-Month": 29.9167, "30-Year": 30}}
        return terms[fc]

    def get_min_mat(self, fc, day_first, day_last):
        min_mat = date.today()
        specs = self.get_specs(fc)
        yrs_to_add, months = divmod(day_first.month + specs['ttm_min']['months'], 12)
        if months == 0:
            months = 12
            min_mat = date(day_first.year + specs['ttm_min']['years'],
            months, day_first.day)
        else:
            min_mat = date(day_first.year + specs['ttm_min']['years'] + yrs_to_add,
                months, day_first.day)
        return min_mat

    def get_max_mat(self, fc, day_first, day_last):
        max_mat = date.today()
        specs = self.get_specs(fc)
        yrs_to_add, months = divmod(day_first.month + specs['ttm_min']['months'], 12)
        dictDaysInMonths = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31,
            8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        try:
            yrs_to_add, months = divmod(day_first.month + specs['ttm_max']['months'], 12)
            if months == 0:
                months = 12
            max_mat = date(day_first.year + specs['ttm_max']['years'] + yrs_to_add,
                months, day_first.day)
        except:
            yrs_to_add, months = divmod(day_last.month + specs['max_to_day_last']['months'], 12)
            if months == 0:
                months = 12
                max_mat = date(day_last.year + specs['max_to_day_last']['years'],
                    months, dictDaysInMonths[months])
            else:
                max_mat = date(day_last.year + specs['max_to_day_last']['years'] + yrs_to_add,
                    months, dictDaysInMonths[months])
        return max_mat

    def get_min_max_mats(self, fc = 'TU', day_first = date(2018, 6, 1), day_last = date(2018, 6, 30)):
        min_mat = self.get_min_mat(fc, day_first, day_last)
        max_mat = self.get_max_mat(fc, day_first, day_last)
        return min_mat, max_mat

    def check_if_when_issued_or_dup(self, t_sec):
        #if len(t_sec["interestRate"]) > 0 and not (t_sec["cusip"] in list_cusip):
        if len(t_sec["interestRate"]) > 0 and not (t_sec["cusip"] in self.list_CUSIPs):
            ust_mat_date = self.get_mat_date(t_sec)
            ttm = (ust_mat_date - date.today()).days / 365.25
            ttm = str('%.2f' % ttm)
            price = self.get_bond_prices(t_sec['cusip'])
            new_bond = bond.bond(ust_mat_date, self.stl_date, float(t_sec['interestRate']) / 100, 2)
            self.value.append({'mat_date': ''.join([t_sec["maturityDate"][0:10]]), 'int_rate': round(float(t_sec["interestRate"]), 3), \
                 'cpns_per_yr': 2, 'ttm': ttm, 'cusip': t_sec["cusip"], 'issue_date': t_sec['issueDate'][0:10], \
                 'yield': new_bond.byld(price), 'price': price})
            self.list_CUSIPs.append(t_sec["cusip"])


    # This method doesn't return a basket. How might you rename it to
    # better reflect what it actually does?
    def define_basket(self, fc = 'TU', fe = 'Jun 2018'):
        '''
        Goes through the list of UST securities gotten previously from the get_web_pg method, and generates a list
        of securities eligible to be delivered into the UST futures contract (passed to the method as fc), which is stored in self.value
        '''
        self.value = [] # start with empty list
        (day1_del_month, day_last_del_month) = self.get_dlv_dates(fe)
        if fc in ['US', 'UB']: # US=bond contract (>=15 yrs to maturity); UB=ultra bond (>=25 yrs to maturity)
            tsy_drct = self.get_web_pg("Bond") # US Treasury securities deliverable into US or UB contracts
        else:
            tsy_drct = self.get_web_pg("Note") # US Treasury securities deliverable into TU (2 yr), FV (5 yr), TY (original 10 yr), TN (ultra 10 yr) contracts
        dict_ust_secs = json.loads(tsy_drct.data.decode("utf-8"))
        dict_terms = self.get_terms(fc)
        dict_specs = self.get_specs(fc)
        self.min_mat_dt, self.max_mat_dt = self.get_min_max_mats(fc, day1_del_month, day_last_del_month)
        list_cusip = []
        for t_sec in dict_ust_secs:
            edge_case = ''
            # check to see if bond's original term satisfies contract specs (mostly applies to TU contract)
            if t_sec["term"] in dict_terms:
                ust_mat_date = self.get_mat_date(t_sec)
                if ust_mat_date >= self.min_mat_dt and ust_mat_date <= self.max_mat_dt:
                    # must check for When Issued (WI) notes and reopenings, as these are not deliverable securities
                    # Also make sure we don't already have the security in our list
                    self.check_if_when_issued_or_dup(t_sec)
                    list_cusip = self.list_CUSIPs


    def get_bond_prices(self, cusip):
        '''
        Opens file with closing prices from date d, then returns closing price
        of US Treasury security identified by cusip. Closing price files are
        in the static\closePx folder
        '''
        f_name = self.get_stl_file_path(self.stl_date)
        #try:
        f_pipe = open(f_name, 'r')
        #except:
        #    print('Could not open pipe to ', f_name)

        prices = xmltodict.parse(f_pipe.read())
        result = 0
        for sec in prices['bpd:FedInvestPriceData']['Prices']['Security']:
            if sec['Cusip'] == cusip:
                if float(sec['EODPrice']) > 0:
                    result = float(sec['EODPrice'])
                else:
                    result = (float(sec['BuyPrice']) + float(sec['SellPrice'])) / 2
        return round(result, 3)

    def get_stl_file_path(self, dt):
        cwd = os.getcwd()
        os_platform = os.name
        if os_platform == 'nt': # case Windows (my dev env)
            return ''.join([cwd, '\static\closePx\securityprice.', str(dt), '.xml'])
        else: # case Linux (my production env)
            if 'public' in cwd:
                return ''.join([cwd, '/static/closePx/securityprice.', str(dt), '.xml'])
            else: return ''.join([cwd, '/public/static/closePx/securityprice.', str(dt), '.xml'])

    def get_last_close_date(self, dt = date.today()):
        last_bus_day = dt
        if dt.weekday() >= 1 and dt.weekday() <= 5: # Tuesday - Saturday
            last_bus_day = dt - timedelta(days = 1)
        elif dt.weekday() == 0: # Monday
            last_bus_day = dt - timedelta(days = 3)
        else:
            last_bus_day = dt - timedelta(days = 2) # Sunday
        return last_bus_day

    def get_latest_stl_date(self, dt = date.today()):
        '''
        Returns the date of the most recent settlement prices file in the
        static/closePx folder.
        '''
        f_name = self.get_stl_file_path(dt)
        while not os.path.isfile(f_name):
            # currently we don't have settlement prices before June 2018
            if dt < date(2018, 6, 1):
                break
            dt = self.get_last_close_date(dt)
            f_name = self.get_stl_file_path(dt)
        return dt

    def set_stl_date(self, dt):
        self.stl_date = dt
