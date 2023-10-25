<div align="center">
  
# iirosebot

一个萌新写的异步垃圾[iirose](https://iirose.com)机器人框架

</div>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/static/v1?label=python&message=3.11.4&color=blue" alt="python">
  </a>
</P>
  
一个python萌新写的iirose机器人屎山框架

> 用户使用本框架做出任何行为作者不可控，产生的后果框架作者概不负责，包括但不限于使用本框架时机器人账户封号等

<details>
<summary>开始使用：</summary>

- ### 1, 克隆本项目
  ```
  git clone https://github.com/XCWQW1/iirosebot.git
  ```


- ### 2, 安装所需库

  进入克隆后的目录执行```pip install -r requirements.txt``` 

- ### 3, 创建或使用已有的iirose账号
  
  >机器人账号标识需向Ruby申请

  访问[iirose](https://iirose.com)创建一个账号，记住用户名以及密码备用

- ### 4, 初始化
  请先执行```python main.py```初始化后再进行操作
  
- ### 4, 配置
  打开 config>config.ini 文件
  按配置文件中的注释配置每个参数，配置文件中的密码不需要md5格式
  
- ### 6, 编写插件 （可选）
	>示例的插件 iirose_example.py iirose_flow_master.py

- ### 7, 启动
  >第一次运行会停止1次要求重启，用于初始化配置文件等
  ```
  python main.py
  ```

</details>


有什么bug或者建议可以提Issues或者进入房间后联系作者

官方房间：沙盒_及其生草的房间(6537c10015add)

<details>
<summary>TODO：</summary>

> 作者很懒，如果你希望添加某个功能可以提交issues，作者看到后会尝试制作
  - #### 插件API
    - [x] 发送房间消息
    - [x] 发送私聊消息
    - [x] 发送弹幕消息
    - [ ] 解析邮件
    - [ ] 发送邮件
    - [x] 引用消息
    - [x] 上传文件
    - [ ] 撤回消息
  
  - #### 框架外部调用
    - [ ] http api
    - [ ] http post
    - [ ] 正向ws
    - [ ] 反向ws
</details>
