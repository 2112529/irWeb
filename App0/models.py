from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from datetime import datetime  # 修改这里的导入
from django.contrib.auth import get_user_model

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    # 创建用户和超级用户的管理器
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)  # 通常您会需要这个字段
    is_staff = models.BooleanField(default=False)  # 对于管理站点的访问
    last_login = models.DateTimeField(null=True, blank=True)  # 添加缺失的字段
    date_joined = models.DateTimeField(default=datetime.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class NewsArticle(models.Model):
    title = models.CharField(max_length=200,null=True)  # 文章标题
    author = models.CharField(max_length=100,null=True)  # 作者
    pub_date = models.DateTimeField(null=True)  # 发布日期
    content = models.TextField(null=True)  # 正文
    keywords = models.TextField(null=True)  # 关键词

    def __str__(self):
        return self.title
    class Meta:
        db_table = 'news_article'

class Postings(models.Model):
    term = models.TextField(primary_key=True, blank=True, null=False)
    df = models.IntegerField(blank=True, null=True)
    docs = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.term
    class Meta:
        db_table = 'postings'

class Knearest(models.Model):
    first = models.IntegerField(blank=True, null=True)
    second = models.IntegerField(blank=True, null=True)
    third = models.IntegerField(blank=True, null=True)
    fourth = models.IntegerField(blank=True, null=True)
    fifth = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'knearest'

class SearchHistory(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.query} at {self.timestamp}"
    class Meta:
        db_table = 'search_history'


class UserInfo(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username
    class Meta:
        db_table = 'user_info'