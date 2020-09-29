# 打通Zabbix告警与企业微信

>Env :Python2 + Python3
python2文件夹下为企业微信的官方API，使用的是python2，尝试改为python3，涉及加密信息，没有修改成功，因此需要python2的环境。
主程序以Python3编写，使用Flask框架。
<br>安装依赖：<br>
>Python2 : pip install -r requirement2.txt <br>
>Python3: pip3 install -r requirement3.txt<br>

## 支持：
>1. zabbix消息推送企业微信
>2. 企业微信上ack或者close zabbix问题
>3. 更多功能开发中

### 系统所有配置信息在 python2/Configure.ini

#### 请将WeChatMessage.py和wechat.ini放置到zabbix告警脚本目录，一般为/usr/lib/zabbix/alertscripts/