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

import requests as requests

skyland_tokens = os.getenv('SKYLAND_TOKEN')


file_save_token = f'{os.path.dirname(__file__)}/INPUT_HYPERGRYPH_TOKEN.txt'

header = {
    'cred': 'cred',
    'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close'
}

header_login = {
    'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close'
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
    v = []
    resp = requests.get(url=binding_url, headers=copy_header(cred)).json()
    if resp['code'] != 0:
        logging.error(f"请求角色列表出现问题：{resp['message']}")
        if resp.get('message') == '用户未登录':
            logging.error(f'用户登录可能失效了，请重新登录！')
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
    characters = get_binding_list(cred)
    for i in characters:
        body = {
            'uid': i.get('uid'),
            'gameId': i.get("channelMasterId")
        }
        resp = requests.post(sign_url, headers=copy_header(cred), json=body).json()
        if resp['code'] != 0:
            logging.error(f'角色{i.get("nickName")}({i.get("channelName")})签到失败了！原因：{resp.get("message")}')
            continue
        awards = resp['data']['awards']
        for j in awards:
            res = j['resource']
            print(
                f'角色{i.get("nickName")}({i.get("channelName")})签到成功，获得了{res["name"]}×{res.get("count") or 1}'
            )


def start(token):
    """
    开始签到
    :param token:
    :return: none
    """
    try:
        cred = login_by_token(token)
        do_sign(cred)
    except Exception as ex:
        logging.error('签到完全失败了！：', exc_info=ex)


def main():
    token_list = skyland_tokens.split(';')
    if len(token_list) != 0:
        for token in token_list:
            start(token)
            print('等待10s')
            time.sleep(10)

    else:
        print('没有设置token')
    print('运行结束!')


if __name__ == "__main__":
    main()
