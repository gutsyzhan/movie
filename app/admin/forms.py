#！/user/bin/python
# -*- coding:utf-8 -*-
# @Time: 2018/8/29 21:17
# @Author: Envse
# @File: forms.py


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from app.models import Admin


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