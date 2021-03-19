'''Фид (feed) – это форма данных (чаще всего XML), которая пре-
доставляет пользователям часто обновляемый контент. Пользователи смогут
подписаться на обновление записей, используя агрегаторы – программное
обеспечение для чтения новостей и получения уведомлений о новых фидах.'''
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post

class LatestPostsFeed(Feed): # унаследовали класс от Feed – класса подсистемы фидов Django
    # Атрибуты title, link и description будут представлены в RSS 
    # элементами <title>, <link> и <description> соответственно
    title = 'Мой блог'
    link = '/blog/'
    description = 'Новый пост на моем блоге'

    def items(self):
        '''объекты, которые будут включены в рассылку;
        берем только последние 5 опубликованных статей для этого фида'''
        return Post.published.all()[:5]

    def item_title(self, item):
        '''заголовок для объекта'''
        return item.title

    def item_description(self, item):
        '''описание для объекта'''
        return truncatewords(item.body, 30) # используем встроенный шаблонный фильтр truncatewords, 
                                            # чтобы ограничить описание статей тридцатью словами
