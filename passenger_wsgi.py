#!/usr/bin/python
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.append(os.getcwd() + '/public')
sys.path.append(os.getcwd() + '/lib/python2.7/site-packages')
#from quickFlaskApp import app as application
print('b4 app')
#from current_UST_list import app as application
from main import app as application
print('after app')
