#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:20
# @Author: Envse
# @File: models.py


from datetime import datetime
from app import db


# 定义会员数据模型
class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 电话号码
    info = db.Column(db.Text)  # 个性简介
    face = db.Column(db.String(255), unique=True)  # 头像
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标志符
    userlogs = db.relationship('UserLog', backref='user')  # 会员日志外键关系
    comments = db.relationship('Comment', backref='user')  # 评论外键关系关联
    moviecols = db.relationship('MovieCol', backref='user')  # 电影收藏外键关系关联

    def __repr__(self):
        return '<User %r>' % self.name


# 定义会员登录日志模型
class UserLog(db.Model):
    __tablename__ = "userlog"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<UserLog %r>' % self.id


# 定义标签数据模型
class Tag(db.Model):
    __tablename__ = "tag"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)   # 编号
    name = db.Column(db.String(100), unique=True)   # 标题
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    movies = db.relationship('Movie', backref='tag')  # 电影外键关系关联

    def __repr__(self):
        return '<Tag %r>' % self.name


# 定义电影数据模型
class Movie(db.Model):
    __tablename__ = "movie"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 电影标题
    url = db.Column(db.String(255), unique=True)  # 电影地址
    info = db.Column(db.Text)  # 电影简介
    logo = db.Column(db.String(255), unique=True)  # 电影封面
    star = db.Column(db.SmallInteger)  # 星级
    playnum = db.Column(db.BigInteger)  # 电影播放量
    commentnum = db.Column(db.BigInteger)  # 电影播放量
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # 所属标签
    area = db.Column(db.String(255))  # 地区
    release_time = db.Column(db.Date)  # 发布时间
    length = db.Column(db.String(100))  # 电影长度
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    comments = db.relationship('Comment', backref='movie')  # 电影评论外键关联
    movieclos = db.relationship('MovieCol', backref='movie')  # 电影收藏外键关联

    def __repr__(self):
        return '<Movie %r>' % self.title


# 定义上映预告数据模型
class Preview(db.Model):
    __tablename__ = "preview"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 电影标题
    logo = db.Column(db.String(255), unique=True)  # 电影封面
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Preview %r>' % self.title


# 定义评论数据模型
class Comment(db.Model):
    __tablename__ = "comment"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 评论内容
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Comment %r>' % self.id


# 定义收藏电影数据模型
class MovieCol(db.Model):
    __tablename__ = "moviecol"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 最近登录时间

    def __repr__(self):
        return '<MovieCol %r>' % self.id


# 定义权限数据模型
class Auth(db.Model):
    __tablename__ = "auth"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    url = db.Column(db.String(255), unique=True)  # 电影地址
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Auth %r>' % self.name


# 定义角色数据模型
class Role(db.Model):
    __tablename__ = "role"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 名称
    auths = db.Column(db.String(600)) # 权限列表
    admins = db.relationship("Admin", backref='role')  # 管理员外键关系关联
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<Role %r>' % self.name


# 定义管理员数据模型
class Admin(db.Model):
    __tablename__ = "admin"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 管理员名称
    pwd = db.Column(db.String(100))  # 管理员密码
    is_super = db.Column(db.SmallInteger)  # 是否为超级管理员，0为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间
    adminlogs = db.relationship('AdminLog', backref='admin')  # 管理员登录日志外键关系关联
    oplogs = db.relationship('OpLog', backref='admin')  # 管理员操作日志外键关系关联

    def __repr__(self):
        return '<Admin %r>' % self.name

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 定义管理员登陆日志数据模型
class AdminLog(db.Model):
    __tablename__ = "adminlog"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<AdminLog %r>' % self.id


# 定义操作日志数据模型
class OpLog(db.Model):
    __tablename__ = "oplog"
    __table_args__ = {"useexisting": True}
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录IP
    reason = db.Column(db.String(600))  # 操作原因
    addtime = db.Column(db.DateTime, index=True, default=datetime.now)  # 添加时间

    def __repr__(self):
        return '<OpLog %r>' % self.id


if __name__ == '__main__':
    db.create_all()