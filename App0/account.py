from django.shortcuts import render, HttpResponse, redirect
from django import forms
from App0 import views
from django.contrib.auth import authenticate

from App0 import models
from App0.models import Users
from django.contrib.auth import logout
from App0.views import index


class UserLoginModelForm(forms.ModelForm):
    class Meta:
        model= models.Users
        fields=["username","password"]

class UserLogupModelForm(forms.ModelForm):
    class Meta:
        model= models.Users
        fields=["username","password","firstname","lastname"]

# 这一次不使用ModelForm,使用Form来实现
class LoginForm(UserLoginModelForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    password = forms.CharField(
        label="密码",
        # render_value=True 表示当提交后,如果密码输入错误,不会自动清空密码输入框的内容
        widget=forms.PasswordInput(attrs={"class": "form-control"}, ),
        required=True,
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return pwd

class LogupForm(UserLogupModelForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    password = forms.CharField(
        label="密码",
        # render_value=True 表示当提交后,如果密码输入错误,不会自动清空密码输入框的内容
        widget=forms.PasswordInput(attrs={"class": "form-control"}, ),
        required=True,
    )
    firstname=forms.CharField(
        label="frstname",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    lastname = forms.CharField(
        label="lastname",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return pwd


def login(request):
    """登录"""
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {"form": form})

    form = LoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 可以在这里保存用户搜索历史，如果需要的话
            return redirect("/search/")
        else:
            form.add_error("password", "用户名或密码错误")
            return render(request, 'login.html', {"form": form})

    return render(request, 'login.html', {"form": form})
def logup(request):
    """注册"""
    if request.method == "GET":
        form = LogupForm()
        return render(request, 'logup.html', {"form": form})

    form = LogupForm(data=request.POST)
    if form.is_valid():
        print("form is valid")
        admin_object = Users.objects.create(**form.cleaned_data)
        auth_object =AuthUser.objects.create(user=admin_object)
        # 如果数据库中没有查询到数据
        if not admin_object:
            # 手动抛出错误显示在"password"字段下
            form.add_error("password", "注册失败")
            return render(request, 'logup.html', {"form": form})
        print("jump to login")
        return redirect("/login/")
    else:
        print("jump to logup")
        return render(request, 'logup.html', {"form": form})

def logout(request):
    logout(request)
    return redirect("/index/")  # 登出后重定向到首页或其他页面
