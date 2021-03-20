from django.urls import path, re_path
from . import views
from .feeds import LatestPostsFeed
'''
    Шаблоны URL’ов позволяют сопоставить адреса с обработчиками.
Шаблон представляет собой комбинацию:
1. строки описывающей адрес;
2. обработчика;
3. необязательного названия, которое даст возможность обращаться к этому шаблону
на всех уровнях проекта.
    Django проходит по порядку по всем шаблонам, пока не найдет первый подходящий, 
т. е. совпадающий с URL’ом запроса. Затем Django сможет импортировать соответствующий 
обработчик и выполнить его, передав внутрь объект запроса HttpRequest и ключевые слова 
или позиционные аргументы.
    Также необходимо добавить определенные здесь шаблоны в конфигурацию URL’ов проекта, 
отредактировав файл urls.py, который находится в каталоге проекта.

'''


app_name = 'blog' # определили пространство имен приложения в переменной app_name;
                  # это позволяет сгруппировать адреса для приложения блога и 
                  # использовать их названия для доступа к ним

urlpatterns = [
    path('', views.post_list, name='post_list'), # вызовет post_list без дополнительных аргументов
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'), # будет передавать аргумент tag_slug
                                                                            # используем преобразователь slug, для того чтобы ограничить
                                                                            # возможные символы URL’а в качестве тега (могут быть использованы
                                                                            # только прописные буквы, числа, нижние подчеркивания и дефисы)
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share', views.post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
]

# Примечание
# Если использование path() и конвертеров не подходит, можно задействовать re_path(). 
# Эта функция позволяет задавать шаблоны URL’ов в виде регулярных выражений.
