#!/usr/bin/env python
from distutils.core import setup

setup(
    name='TWControlYuanData',
    author='Kent Huang',
    version='0.0.1',
    license='MIT',
    description='Crawler to get tw control yuan data',
    long_description=open('README.md').read(),
    scripts=['bin/crawler.py'],
    url='https://github.com/g0v/TWControlYuanData',
    install_requires=[
        'BeautifulSoup4',
        'lxml',
    ],
)
