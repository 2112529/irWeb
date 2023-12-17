from django.shortcuts import render, HttpResponse, redirect
from django import forms
from App0 import views
from django.contrib.auth import authenticate

from App0 import models
from App0.models import Users
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import check_password
from App0.views import index
from django.contrib.auth.decorators import login_required





class LoginForm(forms.Form):  # 直接继承自 forms.Form
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
    )

class LogupForm(forms.ModelForm):
    class Meta:
        model = models.Users
        fields = ["username", "password", "firstname", "lastname"]

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
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

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

        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            # 用户名和密码正确
            auth_login(request, user)
            return redirect("/search/")
        else:
            # 用户名或密码不正确
            form.add_error("password", "用户名或密码错误")
    else:
        # 打印表单的错误
        print("Form errors:", form.errors)
    return render(request, 'login.html', {"form": form})


def logup(request):
    """注册"""
    if request.method == "GET":
        form = LogupForm()
        return render(request, 'logup.html', {"form": form})

    form = LogupForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        firstname = form.cleaned_data['firstname']
        lastname = form.cleaned_data['lastname']
        Users.objects.create_user(username=username, password=password, firstname=firstname, lastname=lastname)
        return redirect("/login/")
    else:
        return render(request, 'logup.html', {"form": form})


@login_required
def user_information(request):
    # 获取当前用户的信息
    user_info = request.user

    # 获取用户的搜索记录等其他信息
    search_history = SearchHistory.objects.filter(user=user_info).order_by('-timestamp')

    return render(request, 'user_information.html', {'user': user_info, 'search_history': search_history})


def logout(request):
    logout(request)
    return redirect("/index/")  # 登出后重定向到首页或其他页面
