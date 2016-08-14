# -*- coding: utf-8 -*-
import pycurl
from io import BytesIO as StringIO
from django.shortcuts import HttpResponse
import json


class Request:
    errstr = None

    def request(self, url, method="GET", data=None, referer_url=None, timeout=False, proxy=None, header=None):
        """\
         发送HTTP请求

         @param string url 请求地址
         @method      请求方式 GET/POST
         @referer_url 请求来源地址
         @data        发送数据
         @timeout     超时时间
         @proxy       HTTP代理服务器
         @return boolean"""
        c = pycurl.Curl()
        if "POST" == method.upper():
            c.setopt(c.POST, True)
            if isinstance(data, str):
                c.setopt(pycurl.POSTFIELDS, data)
            else:
                c.setopt(pycurl.POSTFIELDS, data)
        elif "GET" == method.upper():
            pass
        else:
            self.errstr = "Can't support method \"%s\"" % method
            return HttpResponse('False')
        header_buf = StringIO()
        body_buf = StringIO()
        c.setopt(c.URL, url)
        c.setopt(c.HEADER, False)
        c.setopt(c.FRESH_CONNECT, True)
        # c.setopt(c.RETURNTRANSFER, True)
        c.setopt(c.FORBID_REUSE, True)
        if timeout is not False and timeout > 0:
            c.setopt(c.TIMEOUT, timeout)
        c.setopt(c.HEADERFUNCTION, header_buf.write)
        c.setopt(c.WRITEFUNCTION, body_buf.write)
        if referer_url and referer_url != "":
            c.setopt(c.REFERER_URL, referer_url)
        if header:
            c.setopt(c.HTTPHEADER, header)
        if proxy:
            c.setopt(c.PROXY, proxy)
        try:
            c.perform()
        except (pycurl.error) as e:
            errstr = e
            self.errstr = errstr
            return False
        http_code = c.getinfo(c.HTTP_CODE)
        c.close()
        return {
            "http_code": http_code,
            "header": header_buf.getvalue(),
            "body": body_buf.getvalue(),
            "url": url,
        }


class ZabbixAPI:
    url = None
    timeout = 30
    proxy = False
    errstr = None
    auth_string = None

    def __init__(self, url):
        self.url = url

    def method(self, method, id=1, auth=None, **params):
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": id,
            "auth": auth
        }
        r = Request()
        result = r.request(self.url,
                           method="POST",
                           data=json.dumps(data),
                           header=["Content-Type: application/json"],
                           timeout=self.timeout,
                           proxy=self.proxy)
        # print('zabbixAPI:',result)
        if result is False:
            self.errstr = r.errstr
            return False
        if result["http_code"] != 200:
            self.errstr = "resphonse code " + result["info"]["http_code"]
            return False
        # print result["body"]
        # print(result)
        # print(type(result))
        result = json.loads(result["body"].decode())
        if "error" in result and result["error"]:
            self.errstr = "%s(%s)" % (result["error"]["data"], result["error"]["code"])
            return False
        return result["result"]

    def auth(self, user, password):
        result = self.method("user.login", user=user, password=password, id=1)
        if result is not False:
            self.auth_string = result
        return result

    def get_hostgroup(self, **params):
        return self.method("hostgroup.get", id=2, auth=self.auth_string, **params)

    def get_host(self, **params):
        return self.method("host.get", id=3, auth=self.auth_string, **params)

    def get_graph(self, **params):
        return self.method("graph.get", id=3, auth=self.auth_string, **params)

    def get_item(self, **params):
        return self.method("item.get", id=3, auth=self.auth_string, **params)

    def get_trends(self, **params):
        return self.method("trends.get", id=3, auth=self.auth_string, **params)

    def get_history(self, **params):
        return self.method("history.get", id=3, auth=self.auth_string, **params)


def expand_item_name(name, key):
    pos1 = pos2 = None
    try:
        pos1 = key.index("[")
    except:
        return name
    pos1 += 1
    try:
        pos2 = key.index("]", pos1);
    except:
        return name
    items = key[pos1:pos2].split(",")
    i = len(items)
    while i > 0:
        name = name.replace("$%d" % i, items[i - 1])
        i -= 1
    return name
