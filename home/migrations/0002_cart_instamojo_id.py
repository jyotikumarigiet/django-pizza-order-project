# Generated by Django 4.0.3 on 2022-03-09 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='instamojo_id',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
    ]
