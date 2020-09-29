#!/usr/bin/env python3
# coding:utf-8
import requests
from python2.CorpInfo import *

def TransferIDToName(Userid):
    GetResponse = requests.request("get",
                                   "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret).json()

    access_token = (GetResponse['access_token'])

    get_url = 'https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token=' + access_token+'&userid='+Userid
    GetContent = requests.get(get_url)
    GetContent_ErrorCode = GetContent.json()['errcode']
    if not (GetContent_ErrorCode == 0):
        return -1
    else:
        return (GetContent.json()['name'])




