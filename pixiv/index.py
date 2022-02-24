# -*- coding: utf8 -*-
import json
import traceback
import re
import requests
import random
import urllib
cookie = 'pixiv cookie'


def get(search, p=1, h='0'):
    if not h.isdigit():
        raise Exception('位置参数格式错误')
    if not p.isdigit():
        raise Exception('页数参数格式错误')
    p = int(p)
    h = int(h)
    if h > 60:
        p += h // 60
        h = h % 60
    r = requests.get('https://www.pixiv.net/ajax/search/artworks/' + urllib.parse.quote(search) + f'?&order=popular_d&mode=safe&p={p}&s_mode=s_tag&type=all&lang=zh', headers={
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    })
    data = json.loads(r.text)
    if data['error']:
        raise Exception('搜索请求错误')
    arts = data['body']['illustManga']['data']
    if len(arts) <= 0:
        raise Exception('没有作品')
    h = h - 1 if h else random.randint(0, len(arts) - 1)
    print('搜索:', search, ', 页数:', p, ', 下标:', h)
    total = data['body']['illustManga']['total']
    target = arts[h]

    def transfer(url):
        t1 = re.sub('^https://i.pximg.net/c/.*?/img-master/img/(.*?)_square1200\.(.*?)$',
                    'https://i.pximg.net/img-original/img/\\1.', url)
        if t1 == url:
            return re.sub('^https://i.pximg.net/c/.*?/img/(.*?)_custom1200\.(.*?)$', 'https://i.pximg.net/img-original/img/\\1.', url)
        return t1

    pic = {
        "pid": target['id'],
        "uid": target['userId'],
        "title": target['title'],
        "url": target['url'],
        "username": target['userName']
    }
    ext = 'jpg'
    iurl = transfer(pic['url'])
    url = 'https://service-hzjpf1l4-1301539318.hk.apigw.tencentcs.com/release/download?url=' + iurl + 'jpg'
    print(url)
    down = requests.get(url)
    downdata = json.loads(down.text)
    if downdata.get('code') == -2:
        url = 'https://service-hzjpf1l4-1301539318.hk.apigw.tencentcs.com/release/download?url=' + iurl + 'png'
        print(url)
        ext = 'png'
        down = requests.get(url)
        downdata = json.loads(down.text)
    if downdata.get('code') == -2:
        url = 'https://service-hzjpf1l4-1301539318.hk.apigw.tencentcs.com/release/download?url=' + iurl + 'gif'
        print(url)
        ext = 'gif'
        down = requests.get(url)
        downdata = json.loads(down.text)
    if downdata.get('code') == -2:
        raise Exception(downdata['msg'] + ', 可能是由于图片格式不支持。')
    pic['url'] = downdata['imageUrl']
    pic['ext'] = ext
    pic['pos'] = h + 1
    pic['page'] = p
    pic['total'] = total
    return pic


def image(pid):
    r = requests.get(f'https://www.pixiv.net/artworks/{pid}', headers={
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    })
    url = re.findall('"original":"(.*?)"', r.text)
    if not len(url):
        raise Exception("未找到作品")
    ext = url[0].split('.')[-1]
    title = re.findall('"illustTitle":"(.*?)"', r.text)
    uid = re.findall('"userId":"(.*?)"', r.text)
    username = re.findall('"userName":"(.*?)"', r.text)
    safe = '[R-18]' not in r.text
    if safe:
        down = requests.get(
            'https://service-hzjpf1l4-1301539318.hk.apigw.tencentcs.com/release/download?url=' + url[0])
        downdata = json.loads(down.text)
        if (downdata['code']):
            raise Exception(downdata['msg'])
    data = {
        "url": None if not safe else downdata['imageUrl'],
        "title": title[0],
        "pid": pid,
        "uid": uid[0],
        "username": username[0],
        "ext": ext,
        "safe": safe
    }
    return data


def uid(uid, h='0'):
    if not h.isdigit():
        raise Exception('位置参数格式错误')
    r = requests.get(f'https://www.pixiv.net/ajax/user/{uid}/profile/all', headers={
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    })
    data = json.loads(r.text)
    if (data['error']):
        raise Exception(data['message'])
    arts_r = data['body']['illusts']
    arts = sorted(map(lambda x: int(x), arts_r.keys()), reverse=True)
    lena = len(arts)
    if lena <= 0:
        raise Exception('无作品')
    h = int(h)
    if h <= 0 or h > lena:
        h = random.randint(0, lena - 1)
    else:
        h -= 1
    pid = arts[h]
    data = image(pid)
    data['pos'] = h + 1
    data['total'] = lena
    return data


def usr(nick, h='0'):
    r = requests.get(f'https://www.pixiv.net/search_user.php?s_mode=s_usr&nick={nick}', headers={
        'cookie': cookie,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Microsoft Edge";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    })
    usrs = re.findall('users/(\d+)', r.text)
    if len(usrs) <= 0:
        raise Exception("找不到用户")
    usr = usrs[0]
    return uid(usr, h)


def main_handler(event, context):
    print(event)
    if event['path'] == '/pixiv/search':
        data = {}
        msg = 'ok'
        print('参数', event['queryString'])
        try:
            data = get(event['queryString'].get('search', ''), event['queryString'].get(
                'p', '1'), event['queryString'].get('h', '0'))
            code = 0
        except Exception as e:
            traceback.print_stack()
            print(e)
            msg = str(e)
            code = 1
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "code": code,
                'data': data,
                'msg': msg
            })
        }
    elif event['path'] == '/pixiv/image':
        data = {}
        if not event['queryString'].get('pid'):
            code = 1
            msg = '参数错误'
        else:
            try:
                data = image(event['queryString'].get('pid'))
                code = 0
                msg = 'ok'
            except Exception as e:
                traceback.print_stack()
                print(e)
                msg = str(e)
                code = 1
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "code": code,
                'data': data,
                'msg': msg
            })
        }
    elif event['path'] == '/pixiv/uid':
        data = {}
        if not event['queryString'].get('uid'):
            code = 1
            msg = '参数错误'
        else:
            try:
                data = uid(event['queryString'].get('uid'),
                           event['queryString'].get('h', '0'))
                code = 0
                msg = 'ok'
            except Exception as e:
                traceback.print_stack()
                print(e)
                msg = str(e)
                code = 1
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "code": code,
                'data': data,
                'msg': msg
            })
        }
    elif event['path'] == '/pixiv/user':
        data = {}
        if not event['queryString'].get('user'):
            code = 1
            msg = '参数错误'
        else:
            try:
                data = usr(event['queryString'].get('user'),
                           event['queryString'].get('h', '0'))
                code = 0
                msg = 'ok'
            except Exception as e:
                traceback.print_stack()
                print(e)
                msg = str(e)
                code = 1
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "code": code,
                'data': data,
                'msg': msg
            })
        }
    else:
        return {
            "isBase64Encoded": False,
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "code": -1,
            })
        }
