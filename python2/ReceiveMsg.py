#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: jonyqin
# Created Time: Thu 11 Sep 2014 03:55:41 PM CST
# File Name: Sample.py
# Description: WXBizMsgCrypt 使用demo文件
#########################################################################
from WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import sys
from CorpInfo import *
if __name__ == "__main__":
   #假设企业在公众平台上设置的参数如下
   #sToken = 'uj8bwEKmQYC5SCfIN2fM5t'
   #sEncodingAESKey = 'dqMYVEIX5ai9jtFAYPpVBffPUuIV79k2tAMshIjpiIW'
   #sCorpID ='wwc713f952252fd3fe'
   '''
	------------使用示例二：对用户回复的消息解密---------------
	用户回复消息或者点击事件响应时，企业会收到回调消息，此消息是经过公众平台加密之后的密文以post形式发送给企业，密文格式请参考官方文档
	假设企业收到公众平台的回调消息如下：
	POST /cgi-bin/wxpush? msg_signature=477715d11cdb4164915debcba66cb864d751f3e6&timestamp=1409659813&nonce=1372623149 HTTP/1.1
	Host: qy.weixin.qq.com
	Content-Length: 613
	<xml>	<ToUserName><![CDATA[wx5823bf96d3bd56c7]]></ToUserName><Encrypt><![CDATA[RypEvHKD8QQKFhvQ6QleEB4J58tiPdvo+rtK1I9qca6aM/wvqnLSV5zEPeusUiX5L5X/0lWfrf0QADHHhGd3QczcdCUpj911L3vg3W/sYYvuJTs3TUUkSUXxaccAS0qhxchrRYt66wiSpGLYL42aM6A8dTT+6k4aSknmPj48kzJs8qLjvd4Xgpue06DOdnLxAUHzM6+kDZ+HMZfJYuR+LtwGc2hgf5gsijff0ekUNXZiqATP7PF5mZxZ3Izoun1s4zG4LUMnvw2r+KqCKIw+3IQH03v+BCA9nMELNqbSf6tiWSrXJB3LAVGUcallcrw8V2t9EL4EhzJWrQUax5wLVMNS0+rUPA3k22Ncx4XXZS9o0MBH27Bo6BpNelZpS+/uh9KsNlY6bHCmJU9p8g7m3fVKn28H3KDYA5Pl/T8Z1ptDAVe0lXdQ2YoyyH2uyPIGHBZZIs2pDBS8R07+qN+E7Q==]]></Encrypt>
	<AgentID><![CDATA[218]]></AgentID>
	</xml>

	企业收到post请求之后应该	1.解析出url上的参数，包括消息体签名(msg_signature)，时间戳(timestamp)以及随机数字串(nonce)
	2.验证消息体签名的正确性。	3.将post请求的数据进行xml解析，并将<Encrypt>标签的内容进行解密，解密出来的明文即是用户回复消息的明文，明文格式请参考官方文档
	第2，3步可以用公众平台提供的库函数DecryptMsg来实现。
   '''
   wxcpt = WXBizMsgCrypt(sToken, sEncodingAESKey, sCorpID)
   # sReqMsgSig = HttpUtils.ParseUrl("msg_signature")
   sReqMsgSig = sys.argv[1]
   sReqTimeStamp = sys.argv[2]
   sReqNonce = sys.argv[3]
   sReqData = sys.argv[4]
   ret,sMsg=wxcpt.DecryptMsg( sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
   if( ret!=0 ):
      print "ERR: DecryptMsg ret: " + str(ret)
      sys.exit(1)
   # 解密成功，sMsg即为xml格式的明文
   # TODO: 对明文的处理
   # For example:
   #print(sMsg)
   #print(type(sMsg))
   xml_tree = ET.fromstring(sMsg)
   #print(xml_tree)
   #print(type(xml_tree))
   #print xml_tree.find('Content')
   #print(type (xml_tree.find('Content')))
   MsgType=xml_tree.find('MsgType').text
   if MsgType=='text':
      Content = xml_tree.find('Content')
      FromUserName = xml_tree.find('FromUserName')
      MsgId = xml_tree.find('MsgId')
      ToUserName = xml_tree.find('ToUserName')
      print(Content.text + ',' + FromUserName.text + ',' + MsgType + ',' + ToUserName.text)
   elif MsgType=='event':
      EventKey = xml_tree.find('EventKey')
      try:
         TaskId = xml_tree.find('TaskId')
         FromUserName = xml_tree.find('FromUserName')
         MsgId = '0'
         ToUserName = xml_tree.find('ToUserName')
         print(EventKey.text + ',' + FromUserName.text + ',' + MsgType + ',' + TaskId.text)
      except:
         FromUserName = xml_tree.find('FromUserName')
         MsgId = '0'
         ToUserName = xml_tree.find('ToUserName')
         print(EventKey.text + ',' + FromUserName.text + ',' + MsgType + ',' + 'myproblem')
