"""
库注册指令
"""
import asyncio
import os
import shutil
import platform
import argparse

from iirosebot.main import main as iirosebot_main


def run(args):
    asyncio.run(iirosebot_main())


def init(args):
    data = input("[安装] 是否在目录 {} 下安装iirosebot [Y\\n] ".format(os.getcwd()))
    if data.lower() == "y":
        current_os = platform.system()

        iirosebot_path = shutil.which("iirosebot")
        if iirosebot_path is None:
            iirosebot_path = "iirosebot"

        if current_os == "Linux" or current_os == "Darwin":
            sh_script = """#!/bin/bash
            {}
            read -p "按任意键继续..."
            """.format(iirosebot_path)

            with open('run.sh', 'w') as f:
                f.write(sh_script)

        elif current_os == "Windows":
            bat_script = """@echo off
            iirosebot
            pause
            """.format(iirosebot_path)

            with open('run.bat', 'w') as f:
                f.write(bat_script)

        else:
            sh_script = """#!/bin/bash
            {}
            read -p "按任意键继续..."
            """

            with open('run.sh', 'w') as f:
                f.write(sh_script)

            bat_script = """@echo off
            iirosebot
            pause
            """

            with open('run.bat', 'w') as f:
                f.write(bat_script)

        asyncio.run(iirosebot_main())
    else:
        print('[安装] 安装已中止')
        return


def main():
    parser = argparse.ArgumentParser(description="iirosebot")
    if os.path.exists('config'):
        asyncio.run(iirosebot_main())
    else:
        data = input("是否在目录 {} 下安装iirosebot [Y\\n] ".format(os.getcwd()))
        if data.lower() == "y":
            current_os = platform.system()

            iirosebot_path = shutil.which("iirosebot")
            if iirosebot_path is None:
                iirosebot_path = "iirosebot"

            if current_os == "Linux" or current_os == "Darwin":
                sh_script = """#!/bin/bash
{}
read -p "按任意键继续..."
""".format(iirosebot_path)

                with open('run.sh', 'w') as f:
                    f.write(sh_script)

            elif current_os == "Windows":
                bat_script = """@echo off
iirosebot
pause
""".format(iirosebot_path)

                with open('run.bat', 'w') as f:
                    f.write(bat_script)

            else:
                sh_script = """#!/bin/bash
{}
read -p "按任意键继续..."
"""

                with open('run.sh', 'w') as f:
                    f.write(sh_script)

                bat_script = """@echo off
iirosebot
pause
"""

                with open('run.bat', 'w') as f:
                    f.write(bat_script)

            asyncio.run(iirosebot_main())
        else:
            print('安装已中止')
            return


if __name__ == "__main__":
    main()
