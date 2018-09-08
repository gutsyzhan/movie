#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: views.py


from functools import wraps
from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm, TagForm, MovieForm
from app.models import Admin, Tag, Movie
from app import db, app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime


# 登录装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# 登入
@admin.route('/login/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):  # 切记密码错误时，check_pwd返回false,但此时not check_pwd(data["pwd"])为真！
            flash("密码错误！")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]   # 如果密码正确，就定义session的会话把数据保存到数据库。
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


# 登出
@admin.route('/logout/')
@admin_login_req
def logout():
    session.pop("admin", None)
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd/')
@admin_login_req
def pwd():
    return render_template("admin/pwd.html")


# 后台首页
@admin.route("/")
@admin_login_req
def index():
    return render_template("admin/index.html")


# 添加标签
@admin.route('/tag/add', methods=["GET", "POST"])
@admin_login_req
def tag_add():
    form = TagForm()   # 实例化一个TagForm，然后将form传递到前端页面去。
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["name"]).count()
        # 标签去重
        if tag == 1:
            flash("该标签已经存在了！", "err")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()
        flash("添加标签成功！", "ok")
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 编辑标签
@admin.route('/tag/edit/<int:id>', methods=["GET", "POST"])
@admin_login_req
def tag_edit(id=None):
    form = TagForm()   # 实例化一个TagForm，然后将form传递到前端页面去。
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        # 标签去重
        if tag.name != data["name"] and tag_count == 1:
            flash("该标签已经存在了！", "err")
            return redirect(url_for("admin.tag_edit", id=id))
        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("修改标签成功！", "ok")
        return redirect(url_for("admin.tag_edit", id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 标签列表
@admin.route('/tag/list/<int:page>', methods=["GET"])
@admin_login_req
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)


# 标签删除
@admin.route('/tag/del/<int:id>', methods=["GET"])
@admin_login_req
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签删除成功！", "ok")
    return redirect(url_for("admin.tag_list", page=1))


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]  # 文件后缀
    return filename


# 电影添加
@admin.route('/movie/add', methods=["GET", "POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):  # 如果文件夹不存在
            os.makedirs(app.config["UP_DIR"])  # 新建对应的文件夹
            os.chmod(app.config["UP_DIR"], "rw")  # 给文件夹赋予读写的权限
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        # 把他们进行保存到文件夹下面
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        # 之后的url和logo就是我们修改之后的地址
        movie = Movie(
            title=data["title"],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            playnum=0,
            commentnum=0,
            tag_id=int(data["tag_id"]),
            area=data['area'],
            release_time=data["release_time"],
            length=data["length"],
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功！", "ok")
        return redirect(url_for("admin.movie_add"))
    return render_template("admin/movie_add.html", form=form)


# 电影编辑
@admin.route('/movie/edit/<int:id>', methods=["GET", "POST"])
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()   # 实例化一个TagForm，然后将form传递到前端页面去。
    form.url.validators = []    # 因为是编辑，所以首先必须是非空才需要验证
    form.logo.validators = []
    movie = Movie.query.get_or_404(int(id))
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        # 电影去重，唯一性
        if movie.title != data["title"] and movie_count == 1:
            flash("该影片已经存在了！", "err")
            return redirect(url_for("admin.movie_edit", id=id))
        # 如果文件夹不存在，那么就创建一个文件夹
        if not os.path.exists(app.config["UP_DIR"]):  # 如果文件夹不存在
            os.makedirs(app.config["UP_DIR"])  # 新建对应的文件夹
            os.chmod(app.config["UP_DIR"], "rw")  # 给文件夹赋予读写的权限

        # 如果视频文件修改了，就进行替换
        if form.url.data.filename != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        # 如果图片文件修改了，就进行替换
        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)

        movie.title = data["title"]
        movie.info = data["info"]
        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.length = data["length"]
        movie.area = data["area"]
        movie.release_time = data["release_time"]
        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功！", "ok")
        return redirect(url_for("admin.movie_edit", id=movie.id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


# 电影列表
@admin.route('/movie/list/<int:page>', methods=["GET"])
@admin_login_req
def movie_list(page=None):
    if page is None:
        page = 1
    # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


# 电影删除
@admin.route('/movie/del/<int:id>', methods=["GET"])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("电影删除成功！", "ok")
    return redirect(url_for("admin.movie_list", page=1))


# 上映预告添加
@admin.route('/preview/add')
@admin_login_req
def preview_add():
    return render_template("admin/preview_add.html")


# 上映预告列表
@admin.route('/preview/list')
@admin_login_req
def preview_list():
    return render_template("admin/preview_list.html")


# 会员列表
@admin.route('/user/list')
@admin_login_req
def user_list():
    return render_template("admin/user_list.html")


# 查看会员
@admin.route('/user/view')
@admin_login_req
def user_view():
    return render_template("admin/user_view.html")


# 评论列表
@admin.route('/comment/list')
@admin_login_req
def comment_list():
    return render_template("admin/comment_list.html")


# 电影收藏列表
@admin.route('/moviecol/list')
@admin_login_req
def moviecol_list():
    return render_template("admin/moviecol_list.html")


# 操作日志列表
@admin.route('/oplog/list')
@admin_login_req
def oplog_list():
    return render_template("admin/oplog_list.html")


# 管理员登录日志列表
@admin.route('/adminloginlog/list')
@admin_login_req
def adminloginlog_list():
    return render_template("admin/adminloginlog_list.html")


# 会员登录日志列表
@admin.route('/userloginlog/list')
@admin_login_req
def userloginlog_list():
    return render_template("admin/userloginlog_list.html")


# 添加权限
@admin.route('/auth/add')
@admin_login_req
def auth_add():
    return render_template("admin/auth_add.html")


# 权限列表
@admin.route('/auth/list')
@admin_login_req
def auth_list():
    return render_template("admin/auth_list.html")


# 添加角色
@admin.route('/role/add')
@admin_login_req
def role_add():
    return render_template("admin/role_add.html")


# 角色列表
@admin.route('/role/list')
@admin_login_req
def role_list():
    return render_template("admin/role_list.html")


# 添加管理员
@admin.route('/admin/add')
@admin_login_req
def admin_add():
    return render_template("admin/admin_add.html")


# 管理员列表
@admin.route('/admin/list')
@admin_login_req
def admin_list():
    return render_template("admin/admin_list.html")