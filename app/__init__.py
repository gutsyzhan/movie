#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:15
# @Author: Envse
# @File: __init__.py.py


from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import os
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@127.0.0.5/movie"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS	"] = True
app.config["REDIS_URL"] = "redis://192.168.232.1:6379/0"
app.config["SECRET_KEY"] = "movie_licheetools_top"
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")

rd = FlaskRedis(app)
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
