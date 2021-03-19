from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    '''собственный объект карты сайта; унаследован от Sitemap модуля sitemaps'''
    changefreq = 'weekly' # частота обновления страниц статей
    priority = 0.9        # степень их совпадения с тематикой сайта (максимальное значение – 1)

    def items(self):
        '''Метод items() возвращает QuerySet объектов, которые будут отображаться в карте сайта.
        По умолчанию Django использует метод get_absolute_url() объектов списка, чтобы получать их URL’ы (определен для класса Post).
        Чтобы указать URL для каждого объекта нужно добавить метод location в класс карты сайта.'''
        return Post.published.all()

    def lastmod(self, obj):
        '''принимает каждый объект из результата вызова items() и возвращает время последней модификации статьи'''
        return obj.updated
