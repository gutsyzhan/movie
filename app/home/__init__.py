#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: __init__.py.py


from flask import Blueprint
home = Blueprint("home", __name__)
import app.home.views