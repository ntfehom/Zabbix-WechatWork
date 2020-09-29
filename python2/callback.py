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
	------------使用示例一：验证回调URL---------------
	*企业开启回调模式时，企业号会向验证url发送一个get请求 
	假设点击验证时，企业收到类似请求：
	* GET /cgi-bin/wxpush?msg_signature=5c45ff5e21c57e6ad56bac8758b79b1d9ac89fd3&timestamp=1409659589&nonce=263014780&echostr=P9nAzCzyDtyTWESHep1vC5X9xho%2FqYX3Zpb4yKa9SKld1DsH3Iyt3tP3zNdtp%2B4RPcs8TgAE7OaBO%2BFZXvnaqQ%3D%3D 
	* HTTP/1.1 Host: qy.weixin.qq.com

	接收到该请求时，企业应	1.解析出Get请求的参数，包括消息体签名(msg_signature)，时间戳(timestamp)，随机数字串(nonce)以及公众平台推送过来的随机加密字符串(echostr),
	这一步注意作URL解码。
	2.验证消息体签名的正确性 
	3. 解密出echostr原文，将原文当作Get请求的response，返回给公众平台
	第2，3步可以用公众平台提供的库函数VerifyURL来实现。
   '''
   wxcpt=WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
   #sVerifyMsgSig=HttpUtils.ParseUrl("msg_signature")
   #print sys.argv[0],sys.argv[1],sys.argv[2],sys.argv[3]
   sVerifyMsgSig=sys.argv[1]
   #sVerifyTimeStamp=HttpUtils.ParseUrl("timestamp")
   sVerifyTimeStamp=sys.argv[2]
   #sVerifyNonce=HttpUitls.ParseUrl("nonce")
   sVerifyNonce=sys.argv[3]
   #sVerifyEchoStr=HttpUtils.ParseUrl("echostr")
   sVerifyEchoStr=sys.argv[4]
   ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
   if(ret!=0):
      print "ERR: VerifyURL ret: " + str(ret)
      sys.exit(1)
   #验证URL成功，将sEchoStr返回给企业号
   #HttpUtils.SetResponse(sEchoStr)
   print sEchoStr
