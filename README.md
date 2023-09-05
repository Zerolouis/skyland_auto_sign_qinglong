# skyland_auto_sign_qinglong

适用于青龙面板的森空岛签到脚本

原项目: https://github.com/xxyz30/skyland-auto-sign

## 使用

1. 添加环境变量

   名称: `SKYLAND_TOKEN`

   值: `Token1;Token2;`

   记得添加`;`

2. 青龙面板添加订阅

   地址: `https://github.com/Zerolouis/skyland_auto_sign_qinglong.git`

   推荐定时: `0 0 23 1 * *`

   分支: `master`

3. 运行订阅

4. 默认定时`0 30 8 * * *` , 每天上午8：30运行

## 获取Token

1. 登录[森空岛](https://www.skland.com/)

2. 访问这个网址 https://web-api.skland.com/account/info/hg

   会返回如下信息

   ```json
   {
     "code": 0,
     "data": {
       "content": "Token"
     },
     "msg": "接口会返回您的鹰角网络通行证账号的登录凭证，此凭证可以用于鹰角网络账号系统校验您登录的有效性。泄露登录凭证属于极度危险操作，为了您的账号安全，请勿将此凭证以任何形式告知他人！"
   }
   ```

   data.content即为token

## 通知(可选)

1. 添加环境变量
   
   名称: `SKYLAND_NOTIFY`

   值如下表

   | 值        | 说明       |
   | -------- | -------- |
   | TG       | Telegram |
   | BARK     | bark     |
   | DD       | 钉钉机器人    |
   | FSKEY    | 飞书机器人    |
   | GOBOT    |  QQ机器人        |
   | IGOT     |   iGot 聚合推送       |
   | SERVERJ  |    server 酱      |
   | PUSHDEER |    PushDeer      |
   | PUSHPLUS |    push+ 微信推送      |
   | QMSG     |   qmsg 酱       |
   | QYWXAPP  |   企业微信应用       |
   | QYWXBOT  |  企业微信机器人        |

   仅测试了TG，其他推送方式若有问题请反馈

2. 在青龙面板`脚本管理`中找到本项目的`notify.py`文件，并填入相对应的推送API


## 其他

1. 需要requests包，若报错则在 `依赖管理-python3`，添加`requests`依赖
   
