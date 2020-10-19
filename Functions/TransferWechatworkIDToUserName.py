#!/usr/bin/env python3
# coding:utf-8

"""
通过调用企业微信API，查询企业微信ID对应的企业微信名称（该名称应为实名）
"""

import requests
from Functions.CorpInfo import *

def TransferIDToName(Userid):
    GetResponse = requests.request("get",
                                   "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()

    access_token = (GetResponse['access_token'])

    get_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=' + access_token+'&userid='+Userid
    GetContent = requests.get(get_url,proxies=proxy)
    GetContent_ErrorCode = GetContent.json()['errcode']
    if not (GetContent_ErrorCode == 0):
        return -1
    else:
        return (GetContent.json()['name'])



