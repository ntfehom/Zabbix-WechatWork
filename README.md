# 打通Zabbix告警与企业微信

>Env : Python3 Flask
主程序以Python3编写，使用Flask框架。
<br>安装依赖：<br>
> pip3 install -r requirement.txt<br>

## 支持：
>1. zabbix消息推送企业微信
>2. 企业微信上ack或者close zabbix问题
>3. 更多功能开发中

### 系统所有配置信息在Configure.ini

#### 请将文件夹ZabbixSendMessageScript下的WeChatMessage.py和wechat.ini放置到zabbix告警脚本目录，一般为/usr/lib/zabbix/alertscripts/
#####  要安装本程序，请参阅管理员手册。另，安装完后，请给用户分发用户手册。
