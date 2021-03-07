from django.contrib import admin
'''здесь мы регистрируем модели для добавления их в систему
администрирования Django (использование сайта администрирования
Django не является обязательным!)'''
from .models import Post

admin.site.register(Post)
