#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: views.py


from . import home
from flask import render_template, redirect, url_for, request
from app.home.forms import RegisterForm, LoginForm, UserdetailForm, PwdForm, CommentForm
from app.models import User, UserLog, Preview, Tag, Movie, Comment, MovieCol
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
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]  # 文件后缀
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
@home.route('/comments/<int:page>', methods=["GET"])
@user_login_req
def comments(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == session["user_id"]
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    return render_template("home/comments.html", page_data=page_data)


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


# 添加收藏电影
@home.route('/moviecol/add/', methods=["GET"])
@user_login_req
def moviecol_add():
    mid = request.args.get("mid", "")
    uid = request.args.get("uid", "")
    moviecol = MovieCol.query.filter_by(
        user_id=int(uid),
        movie_id=int(mid),
    ).count()
    if moviecol == 1:
        data = dict(ok=0)
    if moviecol == 0:
        moviecol = MovieCol(
            user_id=int(uid),
            movie_id=int(mid),
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    import json
    return json.dumps(data)


# 收藏电影
@home.route('/moviecol/<int:page>/', methods=["GET"])
@user_login_req
def moviecol(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = MovieCol.query.join(
        Movie
    ).join(
        User
    ).filter(
        User.id == session["user_id"],
        Movie.id == MovieCol.movie_id
    ).order_by(
        MovieCol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/moviecol.html", page_data=page_data)


# 首页
@home.route("/<int:page>/", methods=["GET"])
@home.route("/", methods=["GET"])
def index(page=None):
    tags = Tag.query.all()
    page_data = Movie.query

    movtag = request.args.get("movtag", 0)    # 获取电影标签
    if int(movtag) != 0:
        page_data = page_data.filter_by(tag_id=int(movtag))

    star = request.args.get("star", 0)  # 获取电影星级
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))

    ontime = request.args.get("ontime", 0)  # 获取上映时间
    if int(ontime) != 0:
        if int(ontime) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )

    playnum = request.args.get("playnum", 0)  # 获取播放数量
    if int(playnum) != 0:
        if int(playnum) == 1:
            page_data = page_data.order_by(
                Movie.playnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.playnum.asc()
            )

    commnum = request.args.get("commnum", 0)  # 获取评论数量
    if int(commnum) != 0:
        if int(commnum) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=12)

    p = dict(
        movtag=movtag,
        star=star,
        ontime=ontime,
        playnum=playnum,
        commnum=commnum
    )
    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


# 动画
@home.route('/animation/')
def animation():
    data = Preview.query.all()
    return render_template("home/animation.html", data=data)


# 搜索页面
@home.route('/search/<int:page>/')
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get('key', '')
    movie_count = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/search.html", key=key, movie_count=movie_count, page_data=page_data)


# 详情页面
@home.route('/play/<int:id>/<int:page>/', methods=["GET", "POST"])
def play(id=None, page=None):
    movie = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == movie.id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    movie.playnum = movie.playnum + 1
    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],    # 左侧字段与数据库Comment字段保持一致
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        db.session.add(comment)
        db.session.commit()
        movie.commentnum = movie.commentnum + 1
        db.session.add(movie)
        db.session.commit()
        flash("添加评论成功！", "ok")
        return redirect(url_for("home.play", id=movie.id, page=1))
        movie.commentnum = movie.commentnum+1
    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html", movie=movie, form=form, page_data=page_data)

