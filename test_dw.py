import easytrader

user = easytrader.use('dw')
user.read_config('./dw.json')
user.login()
print dir(user)
print user.balance
