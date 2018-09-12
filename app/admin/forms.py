#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: forms.py


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Auth, Role


# 后台管理员登录表单
class LoginForm(FlaskForm):
    account = StringField(
        label="账号",
        validators=[
            DataRequired("账号不能为空！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号!",
            # "required": "required"   # 注释此处显示forms报错errors信息
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码!",
            # "required": "required"   # 注释此处显示forms报错errors信息
        }
    )

    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("你输入的账号不存在！")


# 添加标签
class TagForm(FlaskForm):
    name = StringField(
        label="名称",
        validators=[
            DataRequired("标签不能为空")
        ],
        description="标签",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！"
        }
    )
    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 添加电影
class MovieForm(FlaskForm):
    title = StringField(
        label="片名",
        validators=[
            DataRequired("片名不能为空")
        ],
        description="片名",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入片名！！"
        }
    )
    url = FileField(
        label="文件",
        validators=[
            DataRequired("请上传文件！")
        ],
        description="文件",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("简介不能为空")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows=": 10,
        }
    )
    logo = FileField(
        label="封面",
        validators=[
            DataRequired("请上传封面！")
        ],
        description="封面",
    )
    star = SelectField(
        label="星级",
        validators=[
            DataRequired("请选择星级！")
        ],
        # 星级是整数型
        coerce=int,
        # 采用下拉选择的方式进行星级的选择
        choices=[(1, "1星级"), (2, "2星级"), (3, "3星级"), (4, "4星级"), (5, "5星级")],
        description="星级",
        render_kw={
            "class": "form-control",
        }
    )
    tag_id = SelectField(
        label="所属标签",
        validators=[
            DataRequired("请选择标签！")
        ],
        # 标签id也是整数型
        coerce=int,
        # 采用列表递归式来取出所有的标签
        choices=[(v.id, v.name)for v in Tag.query.all()],
        description="标签",
        render_kw={
            "class": "form-control",
        }
    )
    area = StringField(
        label="上映地区",
        validators=[
            DataRequired("请输入地区！")
        ],
        description="地区",
        render_kw={
            "class": "form-control",
            "id": "input_area",
            "placeholder": "请输入地区！"
        }
    )
    length = StringField(
        label="电影片长",
        validators=[
            DataRequired("请输入片长！")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "id": "input_length",
            "placeholder": "请输入片长！"
        }
    )
    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请输入上映时间！")
        ],
        description="上映时间",
        render_kw={
            "class": "form-control",
            "id": "input_release_time",
            "placeholder": "请输入上映时间！"
        }
    )
    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 添加预告
class PreviewForm(FlaskForm):
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("预告标题不能为空")
        ],
        description="预告标题",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入预告标题！！"
        }
    )
    logo = FileField(
        label="预告封面",
        validators=[
            DataRequired("请上传预告封面！")
        ],
        description="预告封面",
    )
    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 修改密码
class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("旧密码不能为空！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码!",
            # "required": "required"   # 注释此处显示forms报错errors信息
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("新密码不能为空！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码!",
            # "required": "required"   # 注释此处显示forms报错errors信息
        }
    )
    submit = SubmitField(
        '修改',
        render_kw={
            "class": "btn btn-primary",
        }
    )

    def validate_old_pwd(self, field):
        from flask import session
        pwd = field.data
        name = session["admin"]
        admin = Admin.query.filter_by(
            name=name
        ).first()
        if not admin.check_pwd(pwd):
            raise ValidationError("旧密码输入错误！")


# 添加权限
class AuthForm(FlaskForm):
    name = StringField(
        label="权限名称",
        validators=[
            DataRequired("权限名称不能为空")
        ],
        description="权限名称",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入权限名称！"
        }
    )
    url = StringField(
        label="权限地址",
        validators=[
            DataRequired("权限地址不能为空")
        ],
        description="权限地址",
        render_kw={
            "class": "form-control",
            "id": "input_url",
            "placeholder": "请输入权限地址！"
        }
    )
    submit = SubmitField(
        '修改',
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 添加角色
class RoleFrom(FlaskForm):
    name = StringField(
        label="角色名称",
        validators=[
            DataRequired("角色名称不能为空")
        ],
        description="角色名称",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入角色名称！"
        }
    )
    auths = SelectMultipleField(
        label="权限列表",
        validators=[
            DataRequired("权限列表不能为空")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in Auth.query.all()],   # 数据动态填充选择，采用列表生成式
        description="权限列表",
        render_kw={
            "class": "form-control",
            "id": "input_url",
            "placeholder": "请选择角色列表！"
        }
    )
    submit = SubmitField(
        '修改',
        render_kw={
            "class": "btn btn-primary",
        }
    )


# 添加管理员
class AdminForm(FlaskForm):
    name = StringField(
        label="管理员名称",
        validators=[
            DataRequired("管理员名称不能为空！")
        ],
        description="管理员名称",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员名称!",
            # "required": "required"   # 注释此处显示forms报错errors信息
        }
    )

    pwd = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("管理员密码不能为空！")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码!",
            # "required": "required"   # 注释此处显示forms报错errors信息
        }
    )
    repwd = PasswordField(
        label="管理员重复密码",
        validators=[
            DataRequired("管理员重复密码不能为空！"),
            EqualTo('pwd', message="两次密码不一致！")
        ],
        description="管理员重复密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员重复密码!",
            # "required": "required"   # 注释此处显示forms报错errors信息
        }
    )
    role_id = SelectField(
        label="所属角色",
        validators=[
            DataRequired("请选择所属角色！")
        ],
        # 所属角色是整数型
        coerce=int,
        # 采用下拉选择的方式进行所属角色的选择
        choices=[(v.id, v.name) for v in Role.query.all()],
        description="所属角色",
        render_kw={
            "class": "form-control",
        }
    )

    submit = SubmitField(
        '编辑',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )