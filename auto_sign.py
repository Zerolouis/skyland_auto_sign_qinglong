#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: auto_sign.py(森空岛签到)
Author: Zerolouis
cron: 0 30 8 * * *
new Env('森空岛签到');
Update: 2023/9/5
"""
import json
import logging
import os
import time

import requests
import notify

skyland_tokens = os.getenv('SKYLAND_TOKEN')
skyland_notify = os.getenv('SKYLAND_NOTIFY')

# 消息内容
run_message: str = ''

account_num: int = 1

header = {
    'cred': 'cred',
    'User-Agent': 'Skland/1.1.0 (com.hypergryph.skland; build:100100047; Android 33; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    # 老版本请求头，新版本要验参
    "vName": "1.1.0",
    "vCode": "100100047",
    "dId": "44516b5afabf5518",
    "platform": "1"
    
}

header_login = {
    'User-Agent': 'Skland/1.1.0 (com.hypergryph.skland; build:100100047; Android 33; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close',
    # 老版本请求头，新版本要验参
    "vName": "1.1.0",
    "vCode": "100100047",
    "dId": "44516b5afabf5518",
    "platform": "1"
}

# 签到url
sign_url = "https://zonai.skland.com/api/v1/game/attendance"
# 绑定的角色url
binding_url = "https://zonai.skland.com/api/v1/game/player/binding"

# 使用认证代码获得cred
cred_code_url = "https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code"
# 使用token获得认证代码
grant_code_url = "https://as.hypergryph.com/user/oauth2/v2/grant"

app_code = '4ca99fa6b56cc2ba'

def sendMessage(title:str,content: str,type:str):
    """
    整合消息
    :param title: 标题
    :param content: 内容
    :param type: 类型
    :return: none
    """
    if(skyland_notify):
        type = type.strip()
        match type:
            case 'TG':
                notify.telegram_bot(title,content)
            case 'BARK':
                notify.bark(title,content)
            case 'DD':
                notify.dingding_bot(title,content)
            case 'FSKEY':
                notify.feishu_bot(title,content)
            case 'GOBOT':
                notify.go_cqhttp(title,content)
            case 'GOTIFY':
                notify.gotify(title,content)
            case 'IGOT':
                notify.iGot(title,content)
            case 'SERVERJ':
                notify.serverJ(title,content)
            case 'PUSHDEER':
                notify.pushdeer(title,content)
            case 'PUSHPLUS':
                notify.pushplus_bot(title,content)
            case 'QMSG':
                notify.qmsg_bot(title,content)
            case 'QYWXAPP':
                notify.wecom_app(title,content)
            case 'QYWXBOT':
                notify.wecom_bot(title,content)
            case _:
                pass

 

def copy_header(cred):
    """
    组装请求头
    :param cred: cred
    :return: 拼装后的请求头
    """
    v = json.loads(json.dumps(header))
    v['cred'] = cred
    return v


def login_by_token(token_code):
    """
    通过token登录森空岛获取认证
    :param token_code: 森空岛token
    :return: cred
    """
    try:
        t = json.loads(token_code)
        token_code = t['data']['content']
    except:
        pass
    grant_code = get_grant_code(token_code)
    return get_cred(grant_code)


def get_cred(grant):
    """
    获取cred
    :param grant:认证代码
    :return: cred
    """
    resp = requests.post(cred_code_url, json={
        'code': grant,
        'kind': 1
    }, headers=header_login).json()
    if resp['code'] != 0:
        raise Exception(f'获得cred失败：{resp["messgae"]}')
    return resp['data']['cred']


def get_grant_code(token):
    """
    获取认证代码
    :param token: token
    :return: 认证代码
    """
    resp = requests.post(grant_code_url, json={
        'appCode': app_code,
        'token': token,
        'type': 0
    }, headers=header_login).json()
    if resp['status'] != 0:
        raise Exception(f'使用token: {token} 获得认证代码失败：{resp["msg"]}')
    return resp['data']['code']


def get_binding_list(cred):
    """
    获取绑定的角色
    :param cred: cred
    :return: 返回绑定角色列表
    """
    global run_message
    message:str 
    v = []
    resp = requests.get(url=binding_url, headers=copy_header(cred)).json()
    if resp['code'] != 0:
        message = f"请求角色列表出现问题：{resp['message']}"
        run_message += message + '\n'
        logging.error(message)
        if resp.get('message') == '用户未登录':
            message = f'用户登录可能失效了，请重新登录！'
            run_message += message + '\n'
            logging.error(message)
            return v
    for i in resp['data']['list']:
        if i.get('appCode') != 'arknights':
            continue
        v.extend(i.get('bindingList'))
    return v


def do_sign(cred):
    """
    进行签到
    :param cred: cred
    :return: none
    """
    global run_message
    characters = get_binding_list(cred)
    global account_num
    for i in characters:
        body = {
            'uid': i.get('uid'),
            'gameId': i.get("channelMasterId")
        }
        resp = requests.post(sign_url, headers=copy_header(cred), json=body).json()
        if resp['code'] != 0:
            fail_message:str = f'角色{i.get("nickName")}({i.get("channelName")})签到失败了！原因：{resp.get("message")}'
            run_message +=  f'[账号{account_num}] {fail_message}\n'
            print(fail_message)
            account_num+=1
            continue
        awards = resp['data']['awards']
        for j in awards:
            res = j['resource']
            success_message: str = f'角色{i.get("nickName")}({i.get("channelName")})签到成功，获得了{res["name"]}x{res.get("count") or 1}\n'
            run_message += f'[账号{account_num}] {success_message}\n'
            account_num+=1
            print(success_message)


def start(token):
    """
    开始签到
    :param token:
    :return: none
    """
    global run_message
    try:
        cred = login_by_token(token)
        do_sign(cred)
    except Exception as ex:
        run_message+= f'签到失败: {ex}'
        logging.error('签到完全失败了！: ', exc_info=ex)


def main():
    token_list = skyland_tokens.split(';')
    if len(token_list) != 0:
        for token in token_list:
            if token:
                start(token)
                print('等待10s')
                time.sleep(10)
    else:
        print('没有设置token')
    # 发送消息
    sendMessage('森空岛签到',run_message,skyland_notify.strip())


if __name__ == "__main__":
    main()
