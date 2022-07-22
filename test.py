import requests
import json
import sys
import time
import datetime
import random
import string
import hashlib
import base64


class HTTP:
    server = None
    cookie = None

    @classmethod
    def get_cookie(cls, username, password):
        url = cls.server + "/Action/login"
        passwd_md5 = hashlib.md5(password.encode()).hexdigest()
        passwd_b64 = str(base64.b64encode(password.encode("utf-8")), "utf-8")
        data = {
            "username": username,
            "passwd": passwd_md5,
            "pass": passwd_b64,
            "remember_password": ""
        }
        res = requests.post(url, json=data)
        data = json.loads(res.text)
        if data and data.get('Result') == 10000:
            cookie = requests.utils.dict_from_cookiejar(res.cookies)
            cls.cookie = cookie
        else:
            print("获取 cookie 错误, 请检查输入项是否正确")
            sys.exit()

    @classmethod
    def post(cls, url, data=None, json=None, **kwargs):
        url = cls.server + url
        res = requests.post(url, data, json, cookies=cls.cookie, **kwargs)
        return res


class Wan(object):
    def __init__(self):
        self.id = wan_id

    def show(self):
        url = '/Action/call'
        data = {
            "func_name": "wan",
            "action": "show",
            "param": {
                "id": self.id,
                "TYPE": "support_wisp,total,data"
            }
        }
        res = HTTP.post(url, json=data)
        res_data = res.json()
        data = res_data.get("Data").get("data")
        ip_addr = data[0].get('pppoe_ip_addr')
        if data and ip_addr:
            return ip_addr

    def reconnect(self):
        url = '/Action/call'
        data = {
            "func_name": "wan",
            "action": "link_pppoe_reconnect",
            "param": {
                "id": self.id
            }
        }
        res = HTTP.post(url, json=data)
        res_data = res.json()
        if res_data and res_data.get('Result') == 30000:
            print("重播成功: " + res_data.get("ErrMsg"))
        else:
            print("重播失败: " + res.text)

    def perform(self):
        ip_addr = self.show()
        self.reconnect()
        time.sleep(5)

        re_ip_addr = self.show()
        if ip_addr and re_ip_addr:
            print("ip 地址已更新: ")
            print(ip_addr + ' ---> ' + re_ip_addr)

class User(object):
    def __init__(self):
        self.name = add_name
        self.username = add_username
        self.passwd = None

    def exist(self):
        url = '/Action/call'
        data = {
            "func_name": "pppuser",
            "action": "show",
            "param": {
                "TYPE": "total,data",
                "FINDS": "username,name"
            }
        }
        res = HTTP.post(url, json=data)
        res_data = res.json()
        data = res_data.get("Data").get("data")
        if data:
            for item in data:
                if item.get("username") == self.username:
                    print("用户 {} 已存在".format(item.get("name")))
                    print("账号: " + item.get("username"))
                    print("密码: " + item.get("passwd"))
                    return False
        return True

    def create(self):
        print("创建用户 {}".format(self.username))
        url = '/Action/call'
        passwd = ''.join(random.sample(
            string.ascii_letters + string.digits, 24))
        comment = 'apiCreateUser'
        unix_time = time.mktime(datetime.datetime.now().timetuple())
        data = {
            "func_name": "pppuser",
            "action": "add",
            "param": {
                "username": self.username,
                "passwd": passwd,
                "enabled": "yes",
                "ppptype": "ovpn",
                "bind_ifname": "any",
                "share": 1,
                "auto_mac": 0,
                "upload": 0,
                "download": 0,
                "bind_vlanid": 0,
                "packages": "0",
                "comment": comment,
                "auto_vlanid": 1,
                "ip_addr": "",
                "mac": "",
                "address": "",
                "name": self.name,
                "phone": "",
                "cardid": "",
                "start_time": unix_time,
                "create_time": "",
                "expires": 0
            }
        }
        res = HTTP.post(url, json=data)
        res_data = res.json()
        if res_data and res_data.get('Result') == 30000:
            print("账号: " + self.username)
            print("密码: " + passwd)
        else:
            print("创建失败: " + res_data.get("ErrMsg"))

    def perform(self):
        if self.exist():
            self.create()


class APICreateUser(object):
    def __init__(self):
        self.url = url
        self.server = None
        self.cookie = None
        self.username = username
        self.password = password

    def init_http(self):
        HTTP.server = self.url
        HTTP.get_cookie(self.username, self.password)

    def create_user(self):
        self.init_http()
        user = User()
        user.perform()


class APIPPPoE_Reconnect(object):
    def __init__(self):
        self.url = url
        self.server = None
        self.cookie = None
        self.username = username
        self.password = password
        self.wan_id = wan_id

    def init_http(self):
        HTTP.server = self.url
        HTTP.get_cookie(self.username, self.password)

    def pppoe_reconnect(self):
        self.init_http()
        wan = Wan()
        wan.perform()


if __name__ == '__main__':
    url = 'http://192.168.1.1'
    username = "admin"
    password = "admin"

    # add_name = "测试用户"
    # add_username = "test"

    # api = APICreateUser()
    # api.create_user()

    wan_id = 1  # id1 就是 wan1
    api = APIPPPoE_Reconnect()
    api.pppoe_reconnect()
