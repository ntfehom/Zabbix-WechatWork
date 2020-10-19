#!/usr/bin/env python3
# coding:utf-8
from flask import Flask, request, abort
import logging
from flask.logging import default_handler
from pyzabbix import ZabbixAPI
import warnings
import re
# 以下导入各个文件里的函数
from WeChatAPI.WeChatApiMethod import *
from Functions.SendMsg import *
from Functions.CorpInfo import *
from Functions.TransferWechatworkIDToUserName import *

app = Flask(__name__)
# 去除掉Flask自带日志记录，引入logging。
app.logger.removeHandler(default_handler)

def HandleZabbixEventUpdateRequest(EventID:str,Operations:str,Username:str):
    '''
    EventUpdate.py
    :param EventID: string, like '3711664'
    :param Operations:string, 'ack'/'close'.
    :param Username: Zabbix Username
    :return:
    '''
    #zapi = ZabbixAPI(server=URL)
    #warnings.filterwarnings('ignore')
    #zapi.login(user=UserName, password=PassWord)
    if Operations=='ack':
        AckMessage='用户'+Username+'通过企业微信确认问题ID'+str(EventID)
        try:
            zapi.event.acknowledge(eventids=str(EventID),action='6',message=AckMessage)
            return 0
        except Exception as e:
            (ErrorInfo,ErrorCode)=e.args
            #'Error -32602: Invalid params., Not authorised.', -32602
            if ErrorCode==-32602:
                return -32602
            else:
                RawContent = 'ZABBIX API 程序处理错误，请将以下信息反馈给管理员\nErrorInfo:' + ErrorInfo + '\nErrorCode' + ErrorCode
                return RawContent


    if Operations=='close':
        try:
            CloseMessage = '用户' + Username + '通过企业微信关闭问题ID' + str(EventID)
            zapi.event.acknowledge(eventids=str(EventID), action='1', message=CloseMessage)
            return 0
        except Exception as e:
            (ErrorInfo,ErrorCode)=e.args
            #'Error -32602: Invalid params., Not authorised.', -32602
            if ErrorCode==-32602:
                return -32602
            ErrorString = str(e)
            if ErrorString.find('does not allow manual closing'):
                return ('问题ID ' + str(EventID) + ',触发器未允许手动关闭，请登录zabbix修改相应触发器')
            else:
                return ('问题ID ' + str(EventID) + ',关闭失败，请再次尝试')

def GetHostInventoryFromHostName(HostName):
    InventoryNameList={
        'type':'Type',
        'name':'Name',
        'alias':'Alias',
        'os':'OS',
        'os_full':'OS(Fulldetails)',
        'os_short':'OS(Short)',
        'serialno_a':'Serial number A',
        'serialno_b':'Serialnumber B',
        'software':'Software',
        'location':'Location',
        'location_lat':'Location latitude',
        'location_lon':'Location longitude',
        'model':'Model',
        'hw_arch':'HW architecture',
        'vendor':'Vendor',
        'date_hw_purchase':'Date HW purchased',
        'site_address_a':'Siteaddress A',
        'site_address_b':'Siteaddress B',
        'site_address_c':'Siteaddress C',
        'site_state':'Site state / province',
        'site_country':'Site country',
        'site_zip':'Site ZIP / postal',
        'site_rack':'Site rack location',
        'site_notes':'Site notes',
        'poc_2_name':'Secondary POC name',
        'poc_2_email':'Secondary POC email',
        'poc_2_phone_a':'Secondary POC phone A',
        'poc_2_phone_b':'Secondary POC phone B',
        'poc_2_cell':'Secondary POC cell',
        'poc_2_screen':'Secondary POC screen name',
        'poc_2_notes':'Secondary POC notes'
    }
    Inventorys=[]
    for i in InventoryNameList:
        Inventorys.append(i)
    #zapi = ZabbixAPI(server=URL) # 这里的URL在Functions.CorpInfo定义
    #warnings.filterwarnings('ignore')
    #zapi.login(user=UserName, password=PassWord)

    try:
        InventoryCotent = zapi.host.get(search={'host':[HostName]}, withInventory=1,
                      selectInventory=Inventorys)
    except Exception as e:
        (ErrorInfo, ErrorCode) = e.args
        # 'Error -32602: Invalid params., Not authorised.', -32602
        if ErrorCode == -32602:
            return -32602
        else:
            RawContent ='ZABBIX API 程序处理错误，请将以下信息反馈给管理员\nErrorInfo:'+ErrorInfo+'\nErrorCode'+ErrorCode
            return RawContent


    RawContent = ''
    if InventoryCotent==[]:
        RawContent='未匹配到该主机的信息，可能是主机名填写错误，请检查主机名是否存在于Zabbix系统'
    else:
        InventoryCotent=InventoryCotent[0]['inventory']
        for content in InventoryCotent:
            RawContent=RawContent+InventoryNameList[content]+': '
            RawContent=RawContent+InventoryCotent[content]+'\n'
    return (RawContent)

def ReplyToAllInvolved(ReplyContent,EventID,username):
    #url = URL  # 这里的URL在Functions.CorpInfo定义
    #zapi = ZabbixAPI(server=url)
    #warnings.filterwarnings('ignore')
    #zapi.login(user=UserName, password=PassWord)
    ReplyContent=username+'评论道: '+ReplyContent
    zapi.event.acknowledge(eventids=str(EventID), action='6', message=ReplyContent)
    return 0

def HandleUserSendTxt(text:str,UserID):
    """
    HandleUserSendTxt.py
    接收用户发送的问题后进行合适的处理
    """
    HelpContent='以下为帮助信息：\n发送“ack+空格+故障ID+空格+回复内容”可确认问题，并发送消息给所有跟故障有关的人员（回复内容超过245个字将会被截断，只显示前245个字）\n例: ack 3773316 请XXX立即处理该问题\n'+\
        '发送“info+空格+主机名”可获取主机的硬件信息(主机名可在Zabbix中查询)\n例： info 网站中间件\n发送“help”获取帮助信息'
    CheckAck= re.compile(r'\s*ack\s+(\d+)\s+(.+)', re.I).match(text)
    CheckInfo = re.compile(r'\s*info\s+(.+)', re.I).match(text)
    CheckHelp = re.compile(r'\s*help\s*', re.I).match(text)
    if CheckAck is not None:
        (EventID,ReplyContent)=CheckAck.groups()
        # 当回复内容超过255，Zabbix会无法写入，因此做截断。
        if len(ReplyContent) > 245:
            ReplyContent = ReplyContent[:245]
        username = TransferIDToName(UserID)
        ReplyToAllInvolved(ReplyContent, EventID, username)
        return 0
    elif CheckInfo is not None:
        HostName=CheckInfo.groups()[0]
        RawData = '以下是主机的硬件信息：\n'
        HostInventoryInfo=GetHostInventoryFromHostName(HostName)
        if HostInventoryInfo==-32602:
            return -32602
        RawData = RawData + HostInventoryInfo
        return (RawData)
    elif CheckHelp is not None:
        return (HelpContent)
    else:
        return ('指令不正确\n' + HelpContent)



def ZabbixLogin():
    # Zabbix登录模块，一般用来重新登录Zabbix API
    warnings.filterwarnings('ignore')
    zapi.login(user=UserName, password=PassWord)


@app.route('/', methods=['GET'])
def basic_get():
    try:
        IP = request.headers.get('X-Forwarded-For')
        AttackURL=request.url
        # logger.info('对方IP：'+IP)
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        # 上述几个变量的详细介绍在https://work.weixin.qq.com/api/doc/90000/90135/90930
        callback = HandleCallback(msg_signature, timestamp, nonce, echostr)
        if callback == -1:
            logger.error('回调解析失败，尝试调用HandleCallback时返回-1，访问者IP：' + IP+',攻击方尝试访问URL:'+AttackURL+',Method:GET')
            abort(404)
        return (callback)
    except Exception as e:
        IP = request.headers.get('X-Forwarded-For')
        AttackURL = request.url
        logger.warning('非企业微信合法请求↓，访问者IP：' + IP+',攻击方尝试访问URL:'+AttackURL+',Method:GET')
        logger.warning(e)
        abort(404)


@app.route('/', methods=['POST'])
def basic_post():
    try:
        IP = request.headers.get('X-Forwarded-For')
        AttackURL = request.url
        # logger.info('对方IP：' + IP)
        msg_signature = request.args.get('msg_signature')
        timestamp = request.args.get(('timestamp'))
        nonce = request.args.get('nonce')
        ReqData = request.get_data().decode()
        ReceiveMsg=DecodeMessage(msg_signature,timestamp,nonce,ReqData)
        if ReceiveMsg == -1:
            logger.error('解析用户发送数据失败，尝试调用DecodeMessage时返回-1，访问者IP：' + IP+',攻击方尝试访问URL:'+AttackURL+',Method:POST')
            return ''
        logger.info('ReceiveMsg:'+ReceiveMsg)
        # 在不同条件下，Content有时是消息内容有时是消息触发的动作，具体见WeChatAPI/WeChatApiMethod.py
        (Content,FromUserName,MsgType,ToUserName)=ReceiveMsg.split(',')
        Username = TransferIDToName(FromUserName)
        logging.info('USERID transfered to Username:'+Username)
        if Username == -1:
            logging.warning('该企业微信用户ID未找到用户名，ID为:' + FromUserName)
            return ('')

        # 在不同条件下，ToUserName有时可能是TaskId，具体见python2/ReceiveMsg.py
        # 我们从上面就获取了FromUserName和Content。下面我们要回复消息给微信
        # 此处处理用户发送的消息
        if MsgType == 'text':
            # 处理纯文本事件
            # 调用 HandleUserSendTxt
            #logger.info('开始调用HandleUserSendTxt')

            ReplyContent = HandleUserSendTxt(Content, FromUserName)
            if ReplyContent == -32602:
                # 重新登录Zabbix，再次触发
                logger.warning('调用HandleUserSendTxt时，Zabbix API调用失败错误:' + 'Error -32602: Invalid params., Not authorised.')
                ZabbixLogin()
                ReplyContent = HandleUserSendTxt(Content, FromUserName)
                # 如果发送的是含ack的信息
                if ReplyContent == 0:
                    logger.info('已处理用户发送的消息:' + Content + ',并回复')
                    return ('')
                # 如果重新登录ZABBIX依然报错 - 32602，发送错误日志给用户，本地也记录日志。
                elif ReplyContent == -32602:
                    logger.error('函数HandleUserSendTxt重新登录ZABBIAPI失败')
                    RawData='ZABBIX API 程序处理错误，请将以下信息反馈给管理员\n'+'Error -32602: Invalid params., Not authorised.\n函数：HandleUserSendTxt'
                    try:
                        SendTextToApp(FromUserName, RawData)
                        logger.warning('回复' + FromUserName + '消息,' + '消息内容：' + ReplyContent)
                    except Exception as e:
                        logger.error(e)
                    return ('')
                else:
                    try:
                        SendTextToApp(FromUserName, ReplyContent)
                        logger.warning('回复' + FromUserName + '消息,' + '消息内容：' + ReplyContent)
                    except Exception as e:
                        logger.error(e)
                    return ('')
            # 如果发送的是含ack的信息
            elif ReplyContent == 0:
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
            if ReplyContent==-32602:
                # 重新登录Zabbix，再次触发
                logger.warning('调用HandleZabbixEventUpdateRequest时，Zabbix API调用失败错误:'+'Error -32602: Invalid params., Not authorised.')
                ZabbixLogin()
                ReplyContent = HandleZabbixEventUpdateRequest(EventID, Content, Username)
                #如果重新登录ZABBIX依然报错-32602，发送错误日志给用户，本地也记录日志。
                if ReplyContent==-32602:
                    logger.error('函数HandleZabbixEventUpdateRequest重新登录ZABBIAPI失败')
                    RawData='ZABBIX API 程序处理错误，请将以下信息反馈给管理员\n'+'Error -32602: Invalid params., Not authorised.\n函数：HandleZabbixEventUpdateRequest'
                    SendTextToApp(FromUserName, RawData)
                elif ReplyContent != 0:
                    logger.warning('处理ZabbixAPI确认事件失败，EventID：' + EventID + '，内容：' + Content + '，微信确认用户:' + Username)
                    SendTextToApp(FromUserName, ReplyContent)
                    logger.info('处理ZabbixAPI确认事件失败后，通知用户:' + FromUserName + ', 通知内容:' + ReplyContent)
                else:
                    logger.info('处理ZabbixAPI确认事件更新成功，EventID：' + EventID + '，内容：' + Content + '，微信确认用户:' + Username)
                UpdateTaskCardToApp(FromUserName, ToUserName, Content)
                logger.info('回复' + FromUserName + '卡片消息成功,taskid:' + ToUserName)
            elif ReplyContent != 0:
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
        IP = request.headers.get('X-Forwarded-For')
        AttackURL = request.url
        logger.warning('非企业微信合法请求↓，访问者IP：' + IP+',攻击方尝试访问URL:'+AttackURL+',Method:POST')
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
    #scheduler = APScheduler()
    #scheduler.init_app(app)
    #scheduler.start()
    #server = make_server(host=Host, port=Port, app=app)
    #server.serve_forever()
    # 以上，使用WSGI server封装成生产环境，因此屏蔽了测试环境代码
    ###Zabbix登录代码
    zapi = ZabbixAPI(server=URL)
    warnings.filterwarnings('ignore')
    zapi.login(user=UserName, password=PassWord)

    app.run(host=Host, port=Port, debug=Debug, processes=Processes)
