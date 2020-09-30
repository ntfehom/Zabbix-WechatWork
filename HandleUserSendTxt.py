#!/usr/bin/env python3
# coding:utf-8
from pyzabbix import ZabbixAPI
import warnings
from python2.CorpInfo import *
from TransferWechatworkIDToUserName import *
import re

def HandleUserSendTxt(text:str,UserID):
    HelpContent='以下为帮助信息：\n发送“ack+空格+故障ID+空格+回复内容”可确认问题，并发送消息给所有跟故障有关的人员（回复内容超过245个字将会被截断，只显示前245个字）\n例: ack 3773316 请XXX立即处理该问题\n'+\
        '发送“info+空格+主机名”可获取主机的硬件信息(主机名可在Zabbix中查询)\n例： info 网站中间件\n发送“帮助”或“help”获取帮助信息'
    # 使用正则表达式去除多个空格
    PatternHandleMutipleBlanks= re.compile(r'\s\s+')
    text = re.sub(PatternHandleMutipleBlanks, ' ', text)
    #去除开头可能出现的一个空格
    text=text.strip(' ')
    # flags=re.I表示不区分大小写
    PatternAck= re.compile(r'ack',flags=re.I)
    PatternInfo= re.compile(r'info',flags=re.I)
    PatternMatchBlank = re.compile(r'\s')
    PatternMatchHelpA = re.compile(r'help',flags=re.I)
    PatternMatchHelpB = re.compile(r'帮助')
    # 检测ack
    if re.match(PatternAck,text) is not None:
        text=text[4:]
        BlankLocation=re.search(PatternMatchBlank, text).span()
        EventID=text[:BlankLocation[0]]
        ReplyContent=text[BlankLocation[1]:]
        # 当回复内容超过255，Zabbix会无法写入，因此做截断。
        if len(ReplyContent) > 245:
            ReplyContent = ReplyContent[:245]
        username = TransferIDToName(UserID)
        ReplyToAllInvolved(ReplyContent, EventID, username)
        return 0
    # 检测info
    elif re.match(PatternInfo,text) is not None:
        text=text[5:]
        if re.search(PatternMatchBlank, text) is not None:
            return ('指令不正确\n' + HelpContent)
        else:
            HostName=text
            RawData = '以下是主机的硬件信息：\n'
            RawData = RawData + GetHostInventoryFromHostName(HostName)
            return (RawData)
    # 返回帮助信息
    elif  (re.match(PatternMatchHelpA,text) is not None) or (re.match(PatternMatchHelpB,text) is not None):
        return(HelpContent)
    else:
        return ('指令不正确\n'+HelpContent)




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
    url = URL  # 这里的URL在python2.CorpInfo 定义
    zapi = ZabbixAPI(server=url)
    warnings.filterwarnings('ignore')
    zapi.login(user=UserName, password=PassWord)
    InventoryCotent = zapi.host.get(search={'host':[HostName]}, withInventory=1,
                      selectInventory=Inventorys)
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
    url = URL  # 这里的URL在python2.CorpInfo 定义
    zapi = ZabbixAPI(server=url)
    warnings.filterwarnings('ignore')
    zapi.login(user=UserName, password=PassWord)
    ReplyContent=username+'评论道: '+ReplyContent
    zapi.event.acknowledge(eventids=str(EventID), action='6', message=ReplyContent)
    return 0
