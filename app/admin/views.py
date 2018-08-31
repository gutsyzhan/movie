#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: views.py


from . import admin


@admin.route("/")
def index():
    return "<h1 style='color:blue'>This is admin</h1>"
