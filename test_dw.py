import easytrader
import json

user = easytrader.use('dw')
user.read_config('./dw.json')
user.login()
print dir(user)
import time
time.sleep(2)
print "get_account_info"
print user.get_trade_info()
time.sleep(2)
print user.sh_gdzh
print user.sz_gdzh
time.sleep(2)
print json.dumps(user.get_account_info())
#print "balance"
#print user.balance
