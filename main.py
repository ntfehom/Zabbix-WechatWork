#!/usr/bin/env python3
# coding:utf-8
from flask import Flask, request, abort
import os
import logging
from wsgiref.simple_server import make_server
# 以下导入各个文件里的函数
from SendMsg import *
from TransferWechatworkIDToUserName import *
from EventUpdate import *
from HandleUserSendTxt import *
from python2.CorpInfo import *
from flask.logging import default_handler

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# 去除掉Flask自带日志记录，引入logging。
app.logger.removeHandler(default_handler)


@app.route('/', methods=['GET'])
def basic_get():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        # 上述几个变量的详细介绍在https://work.weixin.qq.com/api/doc/90000/90135/90930
        # 下面，直接调用os来执行python2的代码，读取执行结果，返回回调信息。
        command = '/bin/python /api/python2/callback.py ' + msg_signature + ' ' + timestamp + ' ' + nonce + ' "' + echostr + '"'
        callback = os.popen(command).read()
        return (callback[:-1])
    except Exception as e:
        logger.warning('非企业微信合法请求↓')
        logger.warning(e)
        abort(404)


@app.route('/', methods=['POST'])
def basic_post():
    try:
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        ReqData = request.get_data().decode()
        command = '/bin/python /api/python2/ReceiveMsg.py ' + msg_signature + ' ' + timestamp + ' ' + nonce + ' "' + ReqData + '"'
        ReceiveMsg = os.popen(command).read()
        # 在不同条件下，Content有时是消息内容有时是消息触发的动作，具体见python2/ReceiveMsg.py
        Content = ReceiveMsg[:-1].split(',')[0]
        FromUserName = ReceiveMsg[:-1].split(',')[1]
        Username = TransferIDToName(FromUserName)
        if Username == -1:
            logging.warning('该企业微信用户ID未找到用户名，ID为:' + FromUserName)
            return ('')


        MsgType = ReceiveMsg[:-1].split(',')[2]
        # 在不同条件下，ToUserName有时可能是TaskId，具体见python2/ReceiveMsg.py
        ToUserName = ReceiveMsg[:-1].split(',')[3]
        # 我们从上面就获取了FromUserName和Content。下面我们要回复消息给微信
        # 此处处理用户发送的消息
        if MsgType == 'text':
            # 处理纯文本事件
            # 调用 HandleUserSendTxt
            ReplyContent = HandleUserSendTxt(Content, FromUserName)
            # 如果发送的是含ack的信息
            if ReplyContent == 0:
                logger.info('已处理用户发送的消息:' + Content + ',并回复')
                return ('')
            else:
                try:
                    SendTextToApp(FromUserName, ReplyContent)
                    logger.warning('回复' + FromUserName + '消息,' + '消息内容：' + ReplyContent)
                except Exception as e:
                    logger.error(e)
                return ('')
        # 处理event里面的click事件,就是用户点击微信里的确认开始处理/关闭问题
        if MsgType == 'event' and ToUserName != 'myproblem':
            EventID = ToUserName[:(ToUserName.find('@'))]
            ReplyContent = HandleZabbixEventUpdateRequest(EventID, Content, Username)
            if ReplyContent != 0:
                logger.warning('处理ZabbixAPI确认事件失败，EventID：' + EventID + '，内容：' + Content + '，微信确认用户:' + Username)
                SendTextToApp(FromUserName, ReplyContent)
                logger.info('处理ZabbixAPI确认事件失败后，通知用户:' + FromUserName + ', 通知内容:' + ReplyContent)
            else:
                logger.info('处理ZabbixAPI确认事件更新成功，EventID：' + EventID + '，内容：' + Content + '，微信确认用户:' + Username)
            UpdateTaskCardToApp(FromUserName, ToUserName, Content)
            logger.info('回复' + FromUserName + '卡片消息成功,taskid:' + ToUserName)

        # TODO :获取微信当前用户在zabbix里的所有问题
        # 见GetUserProblem.py，待开发
        if MsgType == 'event' and ToUserName == 'myproblem':
            print('这是myproblem')
        return ('')
    except Exception as e:
        logger.warning('非企业微信合法请求↓')
        logger.warning(e)
        abort(404)


if __name__ == '__main__':
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
    server = make_server(host=Host, port=Port, app=app)
    server.serve_forever()
    # 以上，使用WSGI server封装成生产环境，因此屏蔽了测试环境代码
    # app.run(host=Host, port=Port, debug=Debug, threaded=Threaded)
