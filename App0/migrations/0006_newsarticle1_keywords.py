# Generated by Django 4.2.1 on 2023-12-23 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("App0", "0005_postings1_newsarticle_news_id_newsarticle1_news_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="newsarticle1",
            name="keywords",
            field=models.TextField(null=True),
        ),
    ]
