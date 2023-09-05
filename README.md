# skyland_auto_sign_qinglong

适用于青龙面板的森空岛签到脚本

原项目: https://github.com/xxyz30/skyland-auto-sign

## 使用

1. 添加依赖

   名称: SKYLAND_TOKEN

   值: Token1;Token2;

   记得添加`;`

2. 青龙面板添加订阅

   地址: `https://github.com/Zerolouis/skyland_auto_sign_qinglong.git`

   推荐定时: `0 0 23 1 * *`

   分支：master

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

   
