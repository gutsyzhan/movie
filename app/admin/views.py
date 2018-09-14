#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: views.py


from functools import wraps
from . import admin
from flask import render_template, redirect, url_for, flash, session, request, abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleFrom, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, MovieCol, OpLog, UserLog, AdminLog, Auth, Role
from app import db, app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import datetime


# 上下文处理器
@admin.context_processor
def tpl_extra():
    data = dict(
        online_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data


# 登录装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# 访问权限控制装饰器
def admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin = Admin.query.join(
            Role
        ).filter(
            Role.id == Admin.role_id,
            Admin.id == session["admin_id"]
        ).first()
        auths = admin.role.auths
        auths = list(map(int, auths.split(",")))
        auth_list = Auth.query.all()
        urls = [v.url for v in auth_list for val in auths if val == v.id]
        rule = request.url_rule
        if str(rule) not in urls:
            abort(404)
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
            flash("密码错误！", "err")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]   # 如果密码正确，就定义session的会话把数据保存到数据库。
        session["admin_id"] = admin.id
        adminlog = AdminLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
        )
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


# 登出
@admin.route('/logout/')
@admin_login_req
# @admin_auth
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for('admin.login'))


# 修改密码
@admin.route('/pwd/', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def pwd():
    form = PwdForm()
    if form.validate_on_submit():   # 表单验证，没有这个则无法进行错误信息提示
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html", form=form)


# 后台首页
@admin.route("/")
@admin_login_req
# @admin_auth
def index():
    return render_template("admin/index.html")


# 添加标签
@admin.route('/tag/add', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
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
        oplog = OpLog(
            admin_id=session["admin_id"],
            ip=request.remote_addr,
            reason="添加标签：%s" % data["name"]
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 编辑标签
@admin.route('/tag/edit/<int:id>', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
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
# @admin_auth
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
# @admin_auth
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签删除成功！", "ok")
    return redirect(url_for("admin.tag_list", page=1))


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]  # 文件后缀
    return filename


# 电影添加
@admin.route('/movie/add', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
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
# @admin_auth
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
@admin.route('/movie/list/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
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
# @admin_auth
def movie_del(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("电影删除成功！", "ok")
    return redirect(url_for("admin.movie_list", page=1))


# 上映预告添加
@admin.route('/preview/add', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):  # 如果文件夹不存在
            os.makedirs(app.config["UP_DIR"])  # 新建对应的文件夹
            os.chmod(app.config["UP_DIR"], "rw")  # 给文件夹赋予读写的权限
        logo = change_filename(file_logo)
        # 把他们进行保存到文件夹下面
        form.logo.data.save(app.config["UP_DIR"] + logo)
        # 之后的url和logo就是我们修改之后的地址
        preview = Preview(
            title=data["title"],
            logo=logo,
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功！", "ok")
        return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", form=form)


# 上映预告编辑
@admin.route('/preview/edit/<int:id>', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def preview_edit(id):
    form = PreviewForm()
    form.logo.validators = []  # 如果封面为空，我们就不需要修改
    preview = Preview.query.get_or_404(int(id))
    if request.method == "GET":
        form.title.data = preview.title   # 给title赋初始值
    if form.validate_on_submit():
        data = form.data
        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + preview.logo)
        preview.title = data["title"]
        db.session.add(preview)
        db.session.commit()
        flash("修改预告成功！", "ok")
        return redirect(url_for('admin.preview_edit', id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


# 上映预告列表
@admin.route('/preview/list/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
def preview_list(page=None):
    if page is None:
        page = 1
    # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/preview_list.html", page_data=page_data)


# 预告删除
@admin.route('/preview/del/<int:id>', methods=["GET"])
@admin_login_req
# @admin_auth
def preview_del(id=None):
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("预告删除成功！", "ok")
    return redirect(url_for("admin.preview_list", page=1))


# 会员列表
@admin.route('/user/list/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
def user_list(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/user_list.html", page_data=page_data)
    return render_template("admin/user_list.html")


# 查看会员
@admin.route('/user/view/<int:id>', methods=["GET"])
@admin_login_req
# @admin_auth
def user_view(id=None):
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user)


# 删除会员
@admin.route('/user/del/<int:id>', methods=["GET"])
@admin_login_req
# @admin_auth
def user_del(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("会员删除成功！", "ok")
    return redirect(url_for("admin.user_list", page=1))


# 评论列表
@admin.route('/comment/list/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
def comment_list(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)


# 删除评论
@admin.route('/comment/del/<int:id>', methods=["GET"])
@admin_login_req
# @admin_auth
def comment_del(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("评论删除成功！", "ok")
    return redirect(url_for("admin.comment_list", page=1))


# 电影收藏列表
@admin.route('/moviecol/list/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
def moviecol_list(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = MovieCol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == MovieCol.movie_id,
        User.id == MovieCol.user_id
    ).order_by(
        MovieCol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html", page_data=page_data)


# 删除收藏
@admin.route('/moviecol/del/<int:id>', methods=["GET"])
@admin_login_req
# @admin_auth
def moviecol_del(id=None):
    moviecol = MovieCol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("收藏删除成功！", "ok")
    return redirect(url_for("admin.moviecol_list", page=1))


# 操作日志列表
@admin.route('/oploglist/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
def oplog_list(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = OpLog.query.join(
        Admin
    ).filter(
        Admin.id == OpLog.admin_id
    ).order_by(
        OpLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/oplog_list.html", page_data=page_data)


# 管理员登录日志列表
@admin.route('/adminloginlog/list/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
def adminloginlog_list(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = AdminLog.query.join(
        Admin
    ).filter(
        Admin.id == AdminLog.admin_id
    ).order_by(
        AdminLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/adminloginlog_list.html", page_data=page_data)


# 会员登录日志列表
@admin.route('/userloginlog/list/<int:page>/', methods=["GET"])
@admin_login_req
# @admin_auth
def userloginlog_list(page=None):
    if page is None:
        page = 1
        # 查询的时候关联标签，采用join来加进去,多表关联用filter,过滤用filter_by
    page_data = UserLog.query.join(
        User
    ).filter(
        User.id == UserLog.user_id
    ).order_by(
        UserLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/userloginlog_list.html", page_data=page_data)


# 添加权限
@admin.route('/auth/add', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name=data["name"],
            url=data["url"]
        )
        db.session.add(auth)
        db.session.commit()
        flash("添加权限成功！", "ok")
    return render_template("admin/auth_add.html", form=form)


# 权限列表
@admin.route('/auth/list/<int:page>', methods=["GET"])
@admin_login_req
# @admin_auth
def auth_list(page=None):
    if page is None:
        page = 1
    page_data = Auth.query.order_by(
        Auth.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/auth_list.html", page_data=page_data)


# 权限删除
@admin.route('/auth/del/<int:id>', methods=["GET"])
@admin_login_req
# @admin_auth
def auth_del(id=None):
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash("权限删除成功！", "ok")
    return redirect(url_for("admin.auth_list", page=1))


# 权限编辑
@admin.route('/auth/edit/<int:id>', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def auth_edit(id=None):
    form = AuthForm()   # 实例化一个TagForm，然后将form传递到前端页面去。
    auth = Auth.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        auth.url = data["url"]
        auth.name = data["name"]
        db.session.add(auth)
        db.session.commit()
        flash("修改权限成功！", "ok")
    return render_template("admin/auth_edit.html", form=form, auth=auth)


# 添加角色
@admin.route('/role/add', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def role_add():
    form = RoleFrom()
    if form.validate_on_submit():
        data = form.data
        role = Role(
            name=data["name"],
            auths=','.join(map(str, data["auths"]))  # 采用高阶函数map来生成一个迭代器，然后用''.join()来序列为一个字符串对象
        )
        db.session.add(role)
        db.session.commit()
        flash("添加角色成功！", "ok")
    return render_template("admin/role_add.html", form=form)


# 角色列表
@admin.route('/role/list/<int:page>', methods=["GET"])
@admin_login_req
# @admin_auth
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/role_list.html", page_data=page_data)


# 角色删除
@admin.route('/role/del/<int:id>', methods=["GET"])
@admin_login_req
# @admin_auth
def role_del(id=None):
    role = Role.query.filter_by(id=id).first_or_404()
    db.session.delete(role)
    db.session.commit()
    flash("角色删除成功！", "ok")
    return redirect(url_for("admin.role_list", page=1))


# 角色编辑
@admin.route('/role/edit/<int:id>', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def role_edit(id=None):
    form = RoleFrom()   # 实例化一个TagForm，然后将form传递到前端页面去。
    role = Role.query.get_or_404(id)
    if request.method == "GET":    # 采用get方法对模板中无法直接赋初值的对象进行赋值
        auths = role.auths
        form.auths.data = list(map(int, auths.split(",")))  # form.auths.data为整形数组，而role.auths为一个可变字符串
        # print(list(map(int, auths.split(",")))) # form.auths.data为整形数组，而role.auths为一个可变字符串
        # form.auths.choices
        # list(map(lambda x: x[0], form.auths.choices))==list(map(int, auths.split(",")))
    if form.validate_on_submit():
        data = form.data
        role.name = data["name"]
        role.auths = ','.join(map(str, data["auths"]))
        db.session.add(role)
        db.session.commit()
        flash("修改角色成功！", "ok")
    return render_template("admin/role_edit.html", form=form, role=role)


# 添加管理员
@admin.route('/admin/add', methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def admin_add():
    form = AdminForm()
    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data
        admin = Admin(
            name=data["name"],
            pwd=generate_password_hash(data["pwd"]),
            role_id=data["role_id"],
            is_super=1  # 普通管理员为1
        )
        db.session.add(admin)
        db.session.commit()
        flash("添加管理员成功！", "ok")
    return render_template("admin/admin_add.html", form=form)


# 管理员列表
@admin.route('/admin/list/<int:page>', methods=["GET"])
@admin_login_req
# @admin_auth
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = Admin.query.join(
        Role
    ).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/admin_list.html", page_data=page_data)