#!/usr/bin/env python3
# coding:utf-8
# 整合CorpInfo.ini里的配置信息，传递到所有程序中
AbsolutePath = '/api/Configure.ini'
# 以下两个try为了兼容python2
try:
    import configparser
except:
    import ConfigParser as configparser
config = configparser.ConfigParser()
try:
    config.read(AbsolutePath, encoding='utf-8')
except:
    config.read(AbsolutePath)

# 企业微信相关信息
sToken = config.get('CorpWechat', 'Token')
sEncodingAESKey = config.get('CorpWechat', 'EncodingAESKey')
sCorpID = config.get('CorpWechat', 'CorpID')
CorpID = sCorpID
CorpSecret = config.get('CorpWechat', 'CorpSecret')
AgentID = config.get('CorpWechat', 'AgentID')

# 部署环境网络代理信息
proxy = {'http': config.get('Network', 'Proxy'), 'https': config.get('Network', 'Proxy')}

# zabbix信息
UserName = config.get('ZabbixInfo', 'UserName')
PassWord = config.get('ZabbixInfo', 'PassWord')
URL = config.get('ZabbixInfo', 'URL')

# Web服务器的配置信息
Host = config.get('WebSetting', 'Host')
Port = int(config.get('WebSetting', 'Port'))
# if config.get('WebSetting','Debug') == 0:
#    Debug=False
# elif config.get('WebSetting','Debug') == 1:
#    Debug=True
# else: # 未定义，默认不开启Debug
#    Debug=False
# if config.get('WebSetting','Threaded') == 0:
#    Threaded=False
# elif config.get('WebSetting','Threaded') == 1:
#    Threaded=True
# else: # 未定义，默认开启Threaded
#    Threaded = True
# LogDir,未定义，默认/api/main.log
try:
    LogDir = config.get('WebSetting', 'LogDir')
except:
    LogDir = '/api/main.log'

# LogLevel,未定义，默认'1'
try:
    LogLevel = str(config.get('WebSetting', 'LogLevel'))
except:
    LogLevel = '1'
