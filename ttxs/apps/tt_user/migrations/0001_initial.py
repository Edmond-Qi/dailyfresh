# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('username', models.CharField(unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], error_messages={'unique': 'A user with that username already exists.'}, max_length=30, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active', default=True)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('isDelete', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(to='auth.Group', related_query_name='user', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', blank=True)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', related_query_name='user', related_name='user_set', help_text='Specific permissions for this user.', verbose_name='user permissions', blank=True)),
            ],
            options={
                'db_table': 'df_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('add_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('isDelete', models.BooleanField(default=False)),
                ('receiver', models.CharField(max_length=10)),
                ('addr', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=6)),
                ('phone_number', models.CharField(max_length=11)),
                ('isDefault', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'df_address',
            },
        ),
        migrations.CreateModel(
            name='AreaInfo',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('aParent', models.ForeignKey(to='tt_user.AreaInfo', null=True, blank=True)),
            ],
            options={
                'db_table': 'df_area',
            },
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(to='tt_user.AreaInfo', related_name='city'),
        ),
        migrations.AddField(
            model_name='address',
            name='district',
            field=models.ForeignKey(to='tt_user.AreaInfo', related_name='district'),
        ),
        migrations.AddField(
            model_name='address',
            name='province',
            field=models.ForeignKey(to='tt_user.AreaInfo', related_name='province'),
        ),
    ]
