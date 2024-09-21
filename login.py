import requests
import hashlib
import base64
import yaml
import json
import sys

class HTTP:
    server = None
    cookie = None

    @classmethod
    def load_config(cls, file_path='config.yml'):
        try:
            with open(file_path, 'r') as file:
                config = yaml.safe_load(file)
                cls.server = config['url']
                return config
        except FileNotFoundError as e:
            print("Import error: {}".format(e))
            print("Could not find config file, `cp config_example.yml config.yml`")
            sys.exit(1)

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
        res = requests.post(url, data=data, json=json, cookies=cls.cookie, **kwargs)
        return res

def get_auth_info():
    config = HTTP.load_config()
    HTTP.get_cookie(config['user'], config['password'])
    return {'url': HTTP.server, 'cookies': HTTP.cookie}

if __name__ == "__main__":
    auth_info = get_auth_info()
    if auth_info:
        print("获取到的认证信息:", auth_info)
    else:
        print("未能获取到认证信息")