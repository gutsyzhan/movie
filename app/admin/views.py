#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: views.py


from . import admin
from flask import render_template, redirect, url_for


# 后台首页
@admin.route("/")
def index():
    return render_template("admin/index.html")


# 登入
@admin.route('/login/')
def login():
    return render_template("admin/login.html")


# 登出
@admin.route('/logout/')
def logout():
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd/')
def pwd():
    return render_template("admin/pwd.html")


# 标签编辑
@admin.route('/tag/add')
def tag_add():
    return render_template("admin/tag_add.html")


# 标签列表
@admin.route('/tag/list')
def tag_list():
    return render_template("admin/tag_list.html")


# 电影添加
@admin.route('/movie/add')
def movie_add():
    return render_template("admin/movie_add.html")


# 电影列表
@admin.route('/movie/list')
def movie_list():
    return render_template("admin/movie_list.html")


# 上映预告添加
@admin.route('/preview/add')
def preview_add():
    return render_template("admin/preview_add.html")


# 上映预告列表
@admin.route('/preview/list')
def preview_list():
    return render_template("admin/preview_list.html")


# 会员列表
@admin.route('/user/list')
def user_list():
    return render_template("admin/user_list.html")


# 查看会员
@admin.route('/user/view')
def user_view():
    return render_template("admin/user_view.html")


# 评论列表
@admin.route('/comment/list')
def comment_list():
    return render_template("admin/comment_list.html")


# 电影收藏列表
@admin.route('/moviecol/list')
def moviecol_list():
    return render_template("admin/moviecol_list.html")


# 操作日志列表
@admin.route('/oplog/list')
def oplog_list():
    return render_template("admin/oplog_list.html")


# 管理员登录日志列表
@admin.route('/adminloginlog/list')
def adminloginlog_list():
    return render_template("admin/adminloginlog_list.html")


# 会员登录日志列表
@admin.route('/userloginlog/list')
def userloginlog_list():
    return render_template("admin/userloginlog_list.html")


# 添加权限
@admin.route('/auth/add')
def auth_add():
    return render_template("admin/auth_add.html")


# 权限列表
@admin.route('/auth/list')
def auth_list():
    return render_template("admin/auth_list.html")


# 添加角色
@admin.route('/role/add')
def role_add():
    return render_template("admin/role_add.html")


# 角色列表
@admin.route('/role/list')
def role_list():
    return render_template("admin/role_list.html")


# 添加管理员
@admin.route('/admin/add')
def admin_add():
    return render_template("admin/admin_add.html")


# 管理员列表
@admin.route('/admin/list')
def admin_list():
    return render_template("admin/admin_list.html")