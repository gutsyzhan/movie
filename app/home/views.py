#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: views.py


from . import home
from flask import render_template, redirect, url_for, request
from app.home.forms import RegisterForm, LoginForm, UserdetailForm, PwdForm
from app.models import User, UserLog
from werkzeug.security import generate_password_hash
import uuid
from app import db, app
from flask import flash, session
from functools import wraps
from werkzeug.utils import secure_filename
import os
import datetime
from datetime import datetime


# 登录装饰器
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]  # 文件后缀
    return filename


# 登入
@home.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if not user.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("home.login"))
        session["user"] = user.name
        session["user_id"] = user.id
        userlog = UserLog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(url_for("home.user"))
    return render_template("home/login.html", form=form)


# 登出
@home.route('/logout/')
def logout():
    session.pop("user", None)   # 重定向到前台的登录页面
    session.pop("user_id", None)
    return redirect(url_for('home.login'))


# 会员注册
@home.route('/register/', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("恭喜你注册成功，赶紧登录吧！", "ok")
    return render_template("home/register.html", form=form)


# 会员中心
@home.route('/user/', methods=["GET", "POST"])
@user_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    form.face.validators = []
    if request.method == "GET":    # 给它们赋初始值
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(app.config["FC_DIR"]):
                os.makedirs(app.config["FC_DIR"])
                os.chmod(app.config["FC_DIR"])
            user.face = change_filename(file_face)
            form.face.data.save(app.config["FC_DIR"] + user.face)

        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("该昵称已经存在!", "err")
            return redirect(url_for("home.user"))

        email_count = User.query.filter_by(email=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("该邮箱已经存在!", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("该手机已经存在!", "err")
            return redirect(url_for("home.user"))

        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功!", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


# 修改密码
@home.route('/pwd/', methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():  # 表单验证，没有这个则无法进行错误信息提示
        data = form.data
        user = User.query.filter_by(name=session["user"]).first()
        if not user.check_pwd(data["old_pwd"]):
            flash("旧密码错误！", "err")
            return redirect(url_for('home.pwd'))
        if data["old_pwd"] == data["new_pwd"]:
            flash("新旧密码不能一样！", "err")
            return redirect(url_for('home.pwd'))
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for("home.logout"))
    return render_template("home/pwd.html", form=form)


# 评论记录
@home.route('/comments/')
@user_login_req
def comments():
    return render_template("home/comments.html")


# 登入日志
@home.route('/loginlog/<int:page>/', methods=["GET"])
@user_login_req
def loginlog(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = UserLog.query.filter_by(
        user_id=int(session["user_id"])
    ).order_by(
        UserLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/loginlog.html", page_data=page_data)


# 收藏电影
@home.route('/moviecol/')
@user_login_req
def moviecol():
    return render_template("home/moviecol.html")


# 首页
@home.route('/')
def index():
    return render_template("home/index.html")


# 动画
@home.route('/animation/')
def animation():
    return render_template("home/animation.html")


# 搜索页面
@home.route('/search/')
def search():
    return render_template("home/search.html")


# 详情页面
@home.route('/play/')
def play():
    return render_template("home/play.html")

