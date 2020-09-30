#!/usr/bin/env python3
# coding:utf-8
import sys
import requests
import json
import time
import configparser
import logging


def SendCardMessageToApp(UserId, Subject, Content, task_id):
    """
    发送任务卡片，UserId,Subject,Content,task_id均为string。
    task_id由zabbix的problem ID + @ + 时间戳制成。
    """
    GetResponse = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + CorpID + "&corpsecret=" + CorpSecret,
        proxies=proxy).json()
    access_token = (GetResponse['access_token'])

    rawdata = {
        "touser": UserId,
        "msgtype": "taskcard",
        "agentid": AgentID,
        "taskcard": {
            "title": Subject,
            "description": Content,
            "task_id": task_id,
            "btn": [
                {
                    "key": "ack",
                    "name": "确认开始处理",
                    "replace_name": "已确认处理",
                    "color": "red"
                }
                # 注释掉关闭问题这个按钮，目前暂时用不到关闭问题
                # ,
                # {
                #    "key": "close",
                #    "name": "关闭问题",
                #    "replace_name": "已关闭问题"
                # }
            ]

        },
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata), proxies=proxy)
    #print(PostContent.json())
    #print(rawdata)
    return 0


def SendMarkDownToApp(UserId, Content):
    """
    UserID:str
    Content:str
    发送Zabbix更新或者关闭卡片，Markdown语言支持
    """
    GetResponse = requests.get(
        "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=" + CorpID + "&corpsecret=" + CorpSecret,
        proxies=proxy).json()
    access_token = (GetResponse['access_token'])

    rawdata = {
        "touser": UserId,
        "msgtype": "markdown",
        "agentid": AgentID,
        "markdown": {
            "content": Content
        },
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }

    post_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    PostContent = requests.post(post_url, json.dumps(rawdata), proxies=proxy)
    #print(PostContent.json())
    return 0


if __name__ == '__main__':

    # 以下，读取wechat.ini配置信息
    config = configparser.ConfigParser()
    config.read('/usr/lib/zabbix/alertscripts/WeChat.ini', encoding='utf-8')
    CorpID = config.get('CorpWechat', 'CorpID')
    CorpSecret = config.get('CorpWechat', 'CorpSecret')
    AgentID = config.get('CorpWechat', 'AgentID')
    LogDir = config.get('Log', 'LogDir')
    Proxy = config.get('Network', 'Proxy')
    LogLevel= config.get('Log', 'LogLevel')

    # 开启日志记录
    logger = logging.getLogger()
    # 日志等级
    if LogLevel == '0':
        logger.setLevel(logging.DEBUG)
    elif LogLevel == '1':
        logger.setLevel(logging.INFO)
    elif LogLevel == '2':
        logger.setLevel(logging.WARNING)
    elif LogLevel == '3':
        logger.setLevel(logging.ERROR)
    elif LogLevel == '4':
        logger.setLevel(logging.CRITICAL)
    else:
        # 如无任何定义，默认等级为INFO
        logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LogDir, encoding='utf-8')
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    logger.addHandler(handler)

    # 服务器连接外网时所需的代理地址。
    proxy = {'http': Proxy, 'https': Proxy}
    UserId = sys.argv[1]
    # 去除传递过来的空格
    UserId = UserId.strip(' ')
    Subject = sys.argv[2]
    Message = sys.argv[3]
    # 格式化zabbix传过来的数据
    FormedArray = Message.split('@@@')

    #CurrentTime = time.strftime("%Y-%m-%d %X", time.localtime()) + ' '
    if Subject.find('故障发生') > -1:
        EventID = FormedArray[6]
        Random = int(round(time.time() * 1000))
        task_id = str(str(EventID) + "@" + str(Random))
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
        try:
            SendCardMessageToApp(UserId, Subject, Content, task_id)
        except Exception as e:
            logger.error(e)
        logger.info('满足故障发生\n' + 'UserID:' + UserId + '\n' + 'Subject:' + Subject + '\nContent:' + Content )

    elif Subject.find('故障更新') > -1:
        UpdateDate = FormedArray[0]
        FormedDate = UpdateDate.replace('.', '/', 3)
        UpdateTime = FormedArray[1]
        ProblemName = FormedArray[2]
        HostName = FormedArray[3]
        HostIP = FormedArray[4]
        ProblemSev = FormedArray[5]
        # 注释掉更新者，因为这会让人困惑，更新者永远为ZABBIX的API用户
        # UpdateUser=FormedArray[6]
        UpdateContent = FormedArray[7]
        IsAck = FormedArray[8]
        ProblemID = FormedArray[9]
        Content = '故障更新\n>更新时间：<font color=\"comment\">' + FormedDate + ' - ' + UpdateTime + '</font>\n>故障名：<font color=\"warning\">' + ProblemName + '</font>\n>主机名：<font color=\"comment\">' + \
                  HostName + '</font>\n>主机地址: <font color=\"comment\">' + HostIP + '</font>\n>故障等级: <font color=\"comment\">' + ProblemSev + '</font>\n>更新内容: <font color=\"info\">' + UpdateContent + '</font>\n>是否ACK: <font color=\"warning\">' + IsAck + '</font>\n>Original problem ID：<font color=\"comment\">' + ProblemID + '</font>'
        try:
            SendMarkDownToApp(UserId, Content)
        except Exception as e:
            logger.error(e)
        logger.info('满足故障更新\n' + 'UserID:' + UserId + '\n' + 'Subject:' + Subject + '\nContent:' + Content )

    elif Subject.find('故障解决') > -1:
        ResolveDate = FormedArray[0]
        FormedDate = ResolveDate.replace('.', '/', 3)
        ResolveTime = FormedArray[1]
        ProblemName = FormedArray[2]
        HostName = FormedArray[3]
        HostIP = FormedArray[4]
        ProblemSev = FormedArray[5]
        ProblemID = FormedArray[6]
        Content = '<font color=\"info\">故障解决</font>\n>解决时间：<font color=\"info\">' + FormedDate + ' - ' + ResolveTime + '</font>\n>故障名：<font color=\"info\">' + ProblemName + '</font>\n>主机名：<font color=\"info\">' + \
                  HostName + '</font>\n>主机地址: <font color=\"info\">' + HostIP + '</font>\n>故障等级: <font color=\"info\">' + ProblemSev + '</font>\n>Original problem ID：<font color=\"info\">' + ProblemID + '</font>'
        try:
            SendMarkDownToApp(UserId, Content)
        except Exception as e:
            logger.error(e)
        logger.info('满足故障解决\n' + 'UserID:' + UserId + '\n' + 'Subject:' + Subject + '\nContent:' + Content )

    else:
        logger.warning('无满足\n' + 'UserID:' + UserId + '\n' + 'Subject:' + Subject + '\nMessage:' + Message)
