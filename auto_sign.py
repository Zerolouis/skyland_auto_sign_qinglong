#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: auto_sign.py(森空岛签到)
Author: Zerolouis
cron: 0 30 8 * * *
new Env('森空岛签到');
Update: 2023/9/5
"""
import hashlib
import hmac
import json
import logging
import os
import time
from urllib import parse

import requests
import notify

skyland_tokens = os.getenv('SKYLAND_TOKEN') or ''
skyland_notify = os.getenv('SKYLAND_NOTIFY') or ''

# 消息内容
run_message: str = ''

account_num: int = 1

header = {
    'cred': '',
    'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close'
}

header_login = {
    'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close'
}

# 签名请求头一定要这个顺序，否则失败
# timestamp是必填的,其它三个随便填,不要为none即可
header_for_sign = {
    'platform': '',
    'timestamp': '',
    'dId': '',
    'vName': ''
}

# 参数验证的token
sign_token = ''

# 签到url
sign_url = "https://zonai.skland.com/api/v1/game/attendance"
# 绑定的角色url
binding_url = "https://zonai.skland.com/api/v1/game/player/binding"

# 使用认证代码获得cred
cred_code_url = "https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code"
# 使用token获得认证代码
grant_code_url = "https://as.hypergryph.com/user/oauth2/v2/grant"

app_code = '4ca99fa6b56cc2ba'


def sendMessage(title: str, content: str, type: str):
    """
    整合消息
    :param title: 标题
    :param content: 内容
    :param type: 类型
    :return: none
    """
    if (skyland_notify):
        type = type.strip()
        if type == 'TG':
            notify.telegram_bot(title, content)
        elif type == 'BARK':
            notify.bark(title, content)
        elif type == 'DD':
            notify.dingding_bot(title, content)
        elif type == 'FSKEY':
            notify.feishu_bot(title, content)
        elif type == 'GOBOT':
            notify.go_cqhttp(title, content)
        elif type == 'GOTIFY':
            notify.gotify(title, content)
        elif type == 'IGOT':
            notify.iGot(title, content)
        elif type == 'SERVERJ':
            notify.serverJ(title, content)
        elif type == 'PUSHDEER':
            notify.pushdeer(title, content)
        elif type == 'PUSHPLUS':
            notify.pushplus_bot(title, content)
        elif type == 'QMSG':
            notify.qmsg_bot(title, content)
        elif type == 'QYWXAPP':
            notify.wecom_app(title, content)
        elif type == 'QYWXBOT':
            notify.wecom_bot(title, content)
        else:
            pass


def generate_signature(token: str, path, body_or_query):
    """
    获得签名头
    接口地址+方法为Get请求？用query否则用body+时间戳+ 请求头的四个重要参数（dId，platform，timestamp，vName）.toJSON()
    将此字符串做HMAC加密，算法为SHA-256，密钥token为请求cred接口会返回的一个token值
    再将加密后的字符串做MD5即得到sign
    :param token: 拿cred时候的token
    :param path: 请求路径（不包括网址）
    :param body_or_query: 如果是GET，则是它的query。POST则为它的body
    :return: 计算完毕的sign
    """
    # 总是说请勿修改设备时间，怕不是yj你的服务器有问题吧，所以这里特地-2
    t = str(int(time.time()) - 2)
    token = token.encode('utf-8')
    header_ca = json.loads(json.dumps(header_for_sign))
    header_ca['timestamp'] = t
    header_ca_str = json.dumps(header_ca, separators=(',', ':'))
    s = path + body_or_query + t + header_ca_str
    hex_s = hmac.new(token, s.encode('utf-8'), hashlib.sha256).hexdigest()
    md5 = hashlib.md5(hex_s.encode('utf-8')).hexdigest().encode('utf-8').decode('utf-8')
    logging.info(f'算出签名: {md5}')
    return md5, header_ca


def get_sign_header(url: str, method, body, old_header):
    h = json.loads(json.dumps(old_header))
    p = parse.urlparse(url)
    if method.lower() == 'get':
        h['sign'], header_ca = generate_signature(sign_token, p.path, p.query)
    else:
        h['sign'], header_ca = generate_signature(sign_token, p.path, json.dumps(body))
    for i in header_ca:
        h[i] = header_ca[i]
    return h


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
    global sign_token
    sign_token = resp['data']['token']
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
    message: str
    v = []
    resp = requests.get(binding_url, headers=get_sign_header(binding_url, 'get', None, copy_header(cred))).json()
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
        resp = requests.post(sign_url, headers=get_sign_header(sign_url, 'post', body, copy_header(cred)),
                             json=body).json()
        if resp['code'] != 0:
            fail_message: str = f'角色{i.get("nickName")}({i.get("channelName")})签到失败了！原因：{resp.get("message")}'
            run_message += f'[账号{account_num}] {fail_message}\n'
            print(fail_message)
            account_num += 1
            continue
        awards = resp['data']['awards']
        for j in awards:
            res = j['resource']
            success_message: str = f'角色{i.get("nickName")}({i.get("channelName")})签到成功，获得了{res["name"]}x{res.get("count") or 1}\n'
            run_message += f'[账号{account_num}] {success_message}\n'
            account_num += 1
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
        run_message += f'签到失败: {ex}'
        logging.error('签到完全失败了！: ', exc_info=ex)


def main():
    global run_message
    token_list = skyland_tokens.split(';')
    if len(token_list) != 0:
        for token in token_list:
            if token:
                start(token)
                print('等待10s')
                time.sleep(10)
    else:
        print('没有设置token，请在环境变量里添加至少一个token')
        run_message = '没有设置token，请在环境变量里添加至少一个token'
    # 发送消息
    sendMessage('森空岛签到', run_message, skyland_notify.strip())


if __name__ == "__main__":
    main()
