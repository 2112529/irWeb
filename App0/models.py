from django.db import models

# Create your models here.
class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)

    class Meta:
        db_table = 'users'

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