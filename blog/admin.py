from django.contrib import admin
'''здесь мы регистрируем модели для добавления их в систему
администрирования Django (использование сайта администрирования
Django не является обязательным!)'''
from .models import Post

# admin.site.register(Post) # обычная регистрация модели

@admin.register(Post) # выполняет те же действия, что и функция admin.site.register():
                      # регистрирует декорируемый класс – наследник ModelAdmin
class PostAdmin(admin.ModelAdmin): # создали пользовательский класс -  наследник ModelAdmin
    list_display = ( # атрибут list_display позволяет перечислить поля модели,
                     # которые мы хотим отображать на странице списка
        'title', 'slug', 'author', 'publish', 'status',
    )
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)} # slug генерируется автоматически из поля title
    raw_id_fields = ('author',) # поле author содержит поле поиска, что значительно упрощает
                                # выбор автора из выпадающего списка
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
