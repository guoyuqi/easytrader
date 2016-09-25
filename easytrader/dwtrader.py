# coding: utf-8
from __future__ import division

import json
import os
import random
import tempfile
import urllib

import demjson
import requests
import six

from . import helpers
from .log import log
from .webtrader import NotLoginError
from .webtrader import WebTrader


class DWTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/dw.json'

    def __init__(self):
        super(DWTrader, self).__init__()
        self.account_config = None
        self.s = requests.session()
        self.s.mount('https://', helpers.Ssl3HttpAdapter())

    def login(self, throw=False):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        self.s.headers.update(headers)

        self.s.get(self.config['login_page'], verify=False)

        login_status, result = self.post_login_data()
        if login_status is False and throw:
            raise NotLoginError(result)
        
        return login_status


    def post_login_data(self):
        login_params = dict(
            self.config['login'],
            account=self.account_config['account'],
            tradekey=self.account_config['tradekey'],
            commkey=self.account_config['commkey'],
        )
        login_response = self.s.post(self.config['login_api'], params=login_params)
        print str(login_response.text)
        log.debug('login response: %s' % login_response.text)

        if login_response.text.find('./index.php?auto=1') != -1:
            token_status, token, name = self.get_token()
            if token_status is False:
                
            return True, None
        return False, login_response.text
    
    def get_token(self):
        """获取token和姓名"""
        token_response = self.s.get(self.config['token_api'], verify=False)
        print str(token_response.text)

    def get_balance(self):
        pass


