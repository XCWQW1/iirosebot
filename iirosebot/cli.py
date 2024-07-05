import argparse
import os

from iirosebot.main import main as iirosebot_main


def main():
    parser = argparse.ArgumentParser(description="init/start iirosebot")
    if os.path.exists('config'):
        iirosebot_main()
    else:
        data = input("[安装] 是否在目录 {} 下安装iirosebot [Y\\n] ".format(os.getcwd()))
        if data.lower() == "y":
            iirosebot_main()
        else:
            print('[安装] 安装已中止')
            return


if __name__ == "__main__":
    main()
