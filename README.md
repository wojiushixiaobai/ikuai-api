# ikuai-api

爱快路由器 API

## 使用方法

安装 requests 库
```sh
pip install requests
```

修改 config.yml 文件，填入你的路由器相关信息

```sh
cp config_example.yml config.yml
```

```sh
vim config.yml
```

```yml
url: "http://192.168.9.1"
user: "admin"
password: "admin"
```

### 模块说明
- [x] 账号管理
    - [x] 创建账号
    - [x] 搜索账号
    - [x] 删除账号
    - [x] 停用账号
    - [x] 启用账号

```sh
python account_management.py -h
```
```sh
usage: account_management.py [-h] {create,search,delete,disable,enable} ...

Account Management

positional arguments:
  {create,search,delete,disable,enable}
    create              创建账号
    search              搜索账号
    delete              删除账号
    disable             停用账号
    enable              启用账号

options:
  -h, --help            show this help message and exit
```

## 其他说明

*其他模块有时间再写，欢迎 PR*