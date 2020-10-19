#!/usr/bin/env python3
# coding:utf-8

"""
向企业微信发消息的模块
"""

import requests
import json
from Functions.CorpInfo import *

def SendCardMessageByTaskCardToApp(UserId,Subject,Message,task_id):
    '''
    发送任务卡片，UserId,Subject,Message,task_id均为string。
    task_id由zabbix的problem ID + @ + 时间戳制成。详见WeChatMessage.py
    TODO:本函数的功能已分离至WeChatMessage.py，在整个Flask Web中暂时已无作用，日后将会被删除。
    '''
    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    access_token = (GetResponse['access_token'])
    FormedArray = Message.split('@@@')
    FormedDate = FormedArray[0].replace('.', '/', 3)
    FormedArray[0] = "发生时间：" + FormedDate + ' - '
    FormedArray[1] = FormedArray[1] + '\n'
    FormedArray[2] = "故障名：" + FormedArray[2] + '\n'
    FormedArray[3] = "<div class=\"highlight\">主机名：" + FormedArray[3] + '</div>'
    FormedArray[4] = "<div class=\"highlight\">主机地址: " + FormedArray[4] + '</div>'
    FormedArray[5] = "<div class=\"highlight\">故障等级: " + FormedArray[5] + '</div>\n'
    FormedArray[6] = "<div class=\"gray\">Original problem ID： " + FormedArray[6] + '</div>'
    Content = ''
    for data in FormedArray:
        Content = Content + data
    rawdata = {
        "touser" : UserId,
        "msgtype" : "taskcard",
        "agentid" : AgentID,
        "taskcard" : {
            "title" : Subject,
            "description" : Content,
            "task_id":task_id,
            "btn":[
                {
                    "key": "ack",
                    "name": "确认开始处理",
                    "replace_name": "确认开始处理",
                    "color":"red"
                },
                {
                    "key": "close",
                    "name": "关闭问题",
                    "replace_name": "已关闭问题"
                }
                    ]

                        },
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
}

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    #print(PostContent.json())
    #print(rawdata)
    return 0


def UpdateTaskCardToApp(UserId,TaskID,clicked_key):
    """
    更新任务卡片，当用户点击确认处理时，调用处理程序后，会再调用此函数。
    """
    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    access_token = (GetResponse['access_token'])
    rawdata = {
        "userids" : [UserId],
        "agentid" : AgentID,
        "task_id": TaskID,
        "clicked_key": clicked_key
    }

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/update_taskcard?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    #print(PostContent.json())
    #print(rawdata)
    return 0

def SendTextToApp(UserId,Content):
    '''
        发送纯文本信息
        UserId：String
        Content:String
    '''
    GetResponse = requests.get("https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CorpID+"&corpsecret="+CorpSecret,proxies=proxy).json()
    access_token = (GetResponse['access_token'])
    rawdata = {
        "touser" : UserId,
        "msgtype" : "text",
        "agentid" : AgentID,
        "text" : {
            "content" : Content
            },
        "safe":0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
}
    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata),proxies=proxy)
    #print(PostContent.json())
    #print(rawdata)
    return 0