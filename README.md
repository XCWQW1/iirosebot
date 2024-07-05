<div align="center">
  
# iirosebot

一个适用于 [iirose](https://iirose.com) 的python异步机器人框架

</div> 

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/static/v1?label=python&message=3.11.4&color=blue" alt="python">
  </a>
</P>

<p align="center"><a href="https://github.com/XCWQW1/iirosebot-plugins/blob/main/README.md"><strong>插件列表</strong></a></p>

> 用户使用本框架做出任何行为作者不可控，产生的后果框架作者概不负责，包括但不限于使用本框架时机器人账户被封禁等

### 开始使用：

<details>
<summary>从包管理运行：</summary>

> 需要环境中已安装 3.11.4>=python 并且可以使用 pip 工具

- ### 1, 安装iirosebot
  ```
  pip install iirosebot
  ```

- ### 2, 初始化
  创建或者找到一个合适的文件夹后在文件夹下的命令行\终端中执行 ```iirosebot```
  
- ### 3, 配置 
  打开 config>config.yml 文件
  ```yaml
  bot:
    color: ffffff # 机器人消息颜色
    introduction: '' # 机器人签名
    password: '' # 机器人账户的密码
    room_id: 5ce6a4b520a90  # 机器人登陆后进入的房间id
    username: ''  # 机器人用户名 改名后需修改这里
  log:
    level: INFO # 日志等级 
  other:
    master_id: ''  # 主人唯一标识
  ```
  
- ### 4, 编写\安装插件 （可选）
  > 示例插件 iirose_example.py iirose_flow_master.py 请在仓库iirosebot/plugins下查看

  也可以到[插件仓库](https://github.com/XCWQW1/iirosebot-plugins/blob/main/README.md)里面寻找您喜欢的插件

- ### 5, 启动
  >第一次运行会停止1次要求重启，用于初始化配置文件等
  
  执行 `iirosebot`

- ### 8, 调试
  > 可以私聊机器人发送 `.插件` 获取插件管理菜单，提示无权请检查配置文件中的主人标识是否正确
  
  ### 感谢您的使用

</details>

<details>
<summary>从源码运行：</summary>

- ### 1, 克隆本项目
  ```
  git clone https://github.com/XCWQW1/iirosebot.git
  ```


- ### 2, 安装所需库

  进入克隆后的目录下的iirosebot目录执行```pip install -r requirements.txt``` 

- ### 3, 创建或使用已有的iirose账号
  
  >机器人账号标识需向Ruby申请

  访问[iirose](https://iirose.com)创建一个账号，记住用户名以及密码备用

- ### 4, 初始化
  请先执行```python main.py```初始化后再进行操作
  
- ### 4, 配置
  打开 config>config.yml 文件
  ```yaml
  bot:
    color: ffffff # 机器人消息颜色
    introduction: '' # 机器人签名
    password: '' # 机器人账户的密码
    room_id: 5ce6a4b520a90  # 机器人登陆后进入的房间id
    username: ''  # 机器人用户名 改名后需修改这里
  log:
    level: INFO # 日志等级，一般不用改
  other:
    master_id: ''  # 主人唯一标识
  ```
  
- ### 6, 编写\安装插件 （可选）
	>示例的插件 iirose_example.py iirose_flow_master.py
    也可以到[插件仓库](https://github.com/XCWQW1/iirosebot-plugins/blob/main/README.md)里面寻找您喜欢的插件

- ### 7, 启动
  >第一次运行会停止1次要求重启，用于初始化配置文件等
  
  执行 `python main.py`

- ### 8, 调试
  >可以私聊机器人发送 `.插件` 获取插件管理菜单，提示无权请检查配置文件中的主人标识是否正确
  
  ### 感谢您的使用

</details>


有什么bug或者建议可以提Issues或者进入房间后联系作者

作者唯一标识：[XCWQW233(6533DF3D933BF)](https://iirose.com/#s=6533df3d933bf&act=i:6533df3d933bf)

活跃房间：[伊甸(6547d48b60b2b)](https://iirose.com/#s=6533df3d933bf&r=6547d48b60b2b)

<details>
<summary>TODO：</summary>

  > 作者很懒，如果你希望添加某个功能可以提交issues，作者看到后会尝试制作

  - #### 插件API
    - 消息 
      - [x] 发送房间消息
      - [x] 发送私聊消息
      - [x] 发送弹幕消息
      - [x] 引用消息
      - [x] 上传文件
      - [x] 撤回消息
      - [x] 媒体播放
    - 邮件
      - [x] 解析邮件
      - [x] 发送邮件
    - 股票
      - [x] 股票买入
      - [x] 股票抛出
    - 房间
      - [x] 切换房间
      - [x] 获取房间歌单
      - [x] 获取房间信息 
    - 用户
      - [x] 获取用户信息 
      - [x] 点赞
      - [x] 移动房间(支持密码)
  
  - #### 事件处理
    - 房间
      - [x] 房间消息
      - [x] 用户移动
      - [x] 用户加入
      - [X] 用户退出
      - [x] 撤回消息
    - 私聊
      - [x] 私聊消息
      - [x] 撤回消息
    - 弹幕
      - [x] 弹幕消息
    - 其他
      - [x] 股票信息
      - [x] 大包解析
  
  - #### 框架外部调用
    - [ ] http api
    - [ ] webhook
    - [ ] 正向ws
    - [ ] 反向ws

</details>
