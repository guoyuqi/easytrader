# coding: utf-8
from __future__ import division

import json
import os
import random
import tempfile
import urllib
import re

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

        self.holdings = {}
        self.capital = {}

    def login(self, throw=False):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        }
        self.s.headers.update(headers)

        self.s.get(self.config['login_page'], verify=False)

        login_status, result = self.post_login_data()
        if login_status is False and throw:
            raise NotLoginError(result)

        self.zjzh = self.account_config['account']
        return login_status


    def post_login_data(self):
        login_params = dict(
            self.config['login_params'],
            account=self.account_config['account'],
            tradekey=self.account_config['tradekey'],
            commkey=self.account_config['commkey'],
        )
        login_response = self.s.post(self.config['login_api'], params=login_params)
        #print str(login_response.text)
        log.debug('login response: %s' % login_response.text)

        if login_response.text.find('./index.php?auto=1') != -1:
            token, nickname = self.get_token()
            if token:
                self.token = token
                self.nickname = nickname
                return True, login_response.text
        return False, login_response.text

    def get_token(self):
        """get token and name"""
        token_response = self.s.get(self.config['token_api'], verify=False)
        print self.config['token_re']
        p = re.compile(self.config['token_re'])
        m = p.search(token_response.text)
        if len(m.groups()) == 2:
            return m.group(1), m.group(2)
        return None, None

    def get_trade_info(self):
        """获得上海/深圳股东帐号"""
        trade_response = self.s.get(self.config['trade_api'] % self.token)
        p = re.compile('"gdzh":"([^"]*)"')
        m = p.findall(trade_response.text)
        if len(m) == 2:
            self.sh_gdzh, self.sz_gdzh = m
            return True
        return False

    def get_account_info(self):
        print self.config['account_info_api']
        print self.token

        account_holdings_params = dict(
            self.config['account_holdings_params'],
            zjzh= self.zjzh,
            token_id= self.token,
            gdzh= self.sh_gdzh
        )

        account_holdings_response = self.s.post(self.config['account_info_api'], data=account_holdings_params)
        account_holdings_data = json.loads(account_holdings_response.text.strip())
        if account_holdings_data.get('ret_code', -1) == "0":
            self.holdings = self.format_account_data(account_holdings_data)
            print json.dumps(self.holdings)

        account_capital_params = dict(
            self.config['account_capital_params'],
            zjzh= self.zjzh,
            token_id= self.token,
            gdzh= self.sh_gdzh
        )

        account_capital_response = self.s.post(self.config['account_info_api'], data=account_capital_params)
        account_capital_data = json.loads(account_capital_response.text.strip())
        if account_capital_data.get('ret_code', -1) == "0":
            self.capital = self.format_capital_data(account_capital_data)
            print json.dumps(self.capital)
        return self.capital.update({'item': self.holdings})

    def get_balance(self):
        pass

    def code2name(self, head_code):
        if self.config.get("head_maps").has_key(head_code):
            return self.config.get("head_maps")[head_code]
        return head_code

    def format_capital_data(self, capital_data):
        ret = {}

        for k, v in capital_data.iteritems():
            if self.code2name(k) != k:
                ret[self.code2name(k)] = v

        return ret

    def format_account_data(self, account_data):
        heads = account_data.get('head', [])
        items = account_data.get('item', [])
        ret = []

        for item in items:
            format_item = {}
            for k, v in item.iteritems():
                if self.code2name(k) != k:
                    format_item[self.code2name(k)] = v
            ret.append(format_item)

        return ret


