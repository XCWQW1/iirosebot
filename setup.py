import setuptools

with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requires = fh.read().split("\n")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iirosebot",
    version="1.7.0",
    author="XCWQW1",
    author_email="3539757707@qq.com",
    description="一个用于蔷薇花园(iirose.com)的python机器人框架",
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XCWQW1/iirosebot",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'iirosebot=iirosebot.cli:main',
        ],
    },
    python_requires='>=3.11.4',
)
