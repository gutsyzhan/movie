#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:15
# @Author: Envse
# @File: __init__.py.py


from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@127.0.0.5/movie"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS	"] = True
app.config["SECRET_KEY"] = "movie_licheetools_top"
app.debug = True
db = SQLAlchemy(app)

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")


# 404页面
@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"), 404
