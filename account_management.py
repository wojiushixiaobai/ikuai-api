import requests
import time
import datetime
import random
import string
import argparse
from login import get_auth_info

BASE_URL = "/Action/call"

auth_info = get_auth_info()
url = auth_info['url'] + BASE_URL
cookies = auth_info['cookies']

def generate_unique_username():
    return 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def check_username_exists(username):
    data = {
        "func_name": "pppuser",
        "action": "show",
        "param": {
            "TYPE": "all"
        }
    }
    response = requests.post(url, json=data, cookies=cookies)
    if response.status_code == 200:
        response_data = response.json()
        if response_data["Result"] == 30000:
            users = response_data.get("Data", [])
            for user in users:
                if user["username"] == username:
                    return True
    return False

def create_account(username, passwd=None, name=None, ppptype="any", comment="apiCreate"):
    if not name:
        name = username

    if not passwd:
        passwd = ''.join(random.choices(string.ascii_letters + string.digits, k=24))

    data = {
        "func_name": "pppuser",
        "action": "add",
        "param": {
            "username": username,
            "passwd": passwd,
            "enabled": "yes",
            "ppptype": ppptype,
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
            "name": name,
            "phone": "",
            "cardid": "",
            "ip_type": 0,
            "pppoev6_wan": "",
            "start_time": int(time.mktime(datetime.datetime.now().timetuple())),
            "create_time": "",
            "expires": 0
        }
    }

    response = send_request(data, "创建失败", username)
    if response:
        user_info = {
            'id': response['RowId'],
            'username': username,
            'name': name,
            'passwd': passwd,
            'phone': '',
            'ppptype': ppptype,
            'enabled': 'yes'
        }
        print_user_info([user_info])
    return response

def search_account(keywords=None, show_all=False):
    data = {
        "func_name": "pppuser",
        "action": "show",
        "param": {
            "TYPE": "total,data"
        }
    }

    if not show_all:
        data["param"].update({
            "FINDS": "username,name,address,phone,comment",
            "KEYWORDS": keywords
        })

    response = send_request(data, None, "搜索失败")
    if response and response["Data"]["total"] > 0:
        return response["Data"]["data"]
    return []

def modify_account(action, user_id, username):
    data = {
        "func_name": "pppuser",
        "action": action,
        "param": {
            "id": user_id
        }
    }

    action_msg = {
        "del": "删除",
        "down": "停用",
        "up": "启用"
    }.get(action, "操作")

    response = send_request(data, f"{action_msg}失败", username)
    if response and action != "del":
        user_info = search_account(keywords=username)
        if user_info:
            print_user_info(user_info)

def send_request(data, error_msg, username=None):
    response = requests.post(url, json=data, cookies=cookies)
    if response.status_code == 200:
        response_data = response.json()
        if response_data["Result"] == 30000:
            return response_data
        else:
            print(f"\033[91m账号 {username} {error_msg}: {response_data['ErrMsg']}\033[0m")
            exit(1)
    else:
        print(f"\033[91m请求失败，状态码: {response.status_code}\033[0m")
        exit(1)

def get_search_type(args):
    if args.username:
        return args.username
    elif args.name:
        return args.name
    elif args.phone:
        return args.phone
    else:
        return None

def print_user_info(users):
    print(f"{'id':<5} {'username':<15} {'name':<10} {'passwd':<25} {'phone':<15} {'ppptype':<10} {'enabled':<10}")
    print("-" * 90)
    for user in users:
        print(f"{user['id']:<5} {user['username']:<15} {user['name']:<10} {user['passwd']:<25} {user['phone']:<15} {user['ppptype']:<10} {user['enabled']:<10}")

def add_common_arguments(parser):
    parser.add_argument("--username", type=str, help="按账号操作")
    parser.add_argument("--name", type=str, help="按用户姓名操作")
    parser.add_argument("--phone", type=str, help="按电话操作")

def handle_modify_command(args, action):
    keywords = get_search_type(args)
    if not keywords:
        print("请提供搜索关键词")
        return

    search_result = search_account(keywords=keywords)
    if search_result:
        if len(search_result) == 1:
            user_info = search_result[0]
            modify_account(action=action, user_id=user_info["id"], username=user_info["username"])
        else:
            print("找到多个匹配的用户，请提供更具体的信息: ")
            print_user_info(search_result)
    else:
        print("未能找到账号")

def main():
    parser = argparse.ArgumentParser(description="Account Management")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create", help="创建账号")
    create_parser.add_argument("-u", "--username", type=str, required=True, help="账号")
    create_parser.add_argument("-p", "--passwd", type=str, help="密码")
    create_parser.add_argument("--name", type=str, help="用户姓名")
    create_parser.add_argument(
        "-t", "--ppptype", type=str, choices=[
            "any", "web", "pppoe", "pptp", "l2tp", "ovpn", "ike"
        ], default="any", help=(
            "认证类型 "
            "(any: 不限, web: WEB-帐号, pppoe: PPPoE, pptp: PPTP, "
            "l2tp: L2TP, ovpn: OpenVPN, ike: IKEv2)"
        )
    )
    create_parser.add_argument("--comment", type=str, default="apiCreate", help="备注")

    search_parser = subparsers.add_parser("search", help="搜索账号")
    add_common_arguments(search_parser)
    search_parser.add_argument("--all", action="store_true", help="显示所有账号")

    delete_parser = subparsers.add_parser("delete", help="删除账号")
    add_common_arguments(delete_parser)

    disable_parser = subparsers.add_parser("disable", help="停用账号")
    add_common_arguments(disable_parser)

    enable_parser = subparsers.add_parser("enable", help="启用账号")
    add_common_arguments(enable_parser)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "create":
        create_account(username=args.username, passwd=args.passwd, name=args.name, ppptype=args.ppptype, comment=args.comment)
    elif args.command == "search":
        search_result = search_account(show_all=args.all) if args.all else search_account(keywords=get_search_type(args))
        if search_result:
            print_user_info(search_result)
        else:
            print("未能找到账号")
    elif args.command == "delete":
        handle_modify_command(args, "del")
    elif args.command == "disable":
        handle_modify_command(args, "down")
    elif args.command == "enable":
        handle_modify_command(args, "up")

if __name__ == "__main__":
    main()