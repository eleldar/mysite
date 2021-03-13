'''модели данных приложения. В любом Django-приложении
должен быть этот файл, но он может оставаться пустым'''
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class PublishedManager(models.Manager):
    '''Собственный менеджер модели; альтернатива objects'''
    def get_queryset(self):
        '''Метод get_queryset() менеджера по умолчанию возвращает QuerySet, 
        который будет выполняться; мы его переопределили и добавили фильтр над результирующим QuerySet’ом'''
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    # для выбора определенного поля в качестве перичного ключа следует в его параметре указать primary_key=True; по умолчанию -  id
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    title = models.CharField(max_length=250) # заголовок статьи
    slug = models.SlugField(max_length=250, unique_for_date='publish') # короткое название, содержащее только буквы, цифры и нижние подчеркивания или дефисы.
                                                                       # Используем slug для построения семантических URL’ов (friendly URLs) для статей.
                                                                       # Параметр unique_for_date позволяет формировать уникальные URL’ы, используя дату публикации
                                                                       # статей и slug. Django будет предотвращать создание нескольких статей с одинаковым слагом
                                                                       # в один и тот же день
    author = models.ForeignKey(User, on_delete=models.CASCADE,  # внешний ключ - отношение «один ко многим;
                               related_name='blog_posts')       # каждая статья имеет автора, причем каждый пользователь может быть автором любого количества статей;
                                                                # Для этого поля в базе данных создается внешний ключ, используя первичный ключ связанной модели (User подсистемы аутентификации Django).
                                                                # Параметр on_delete определяет поведение при удалении связанного объекта.
                                                                # Используя CASCADE при удалении связанного пользователя из базы данных удаляются написанные им статьи.
    body = models.TextField() # содержание статьи
    publish = models.DateTimeField(default=timezone.now)    # дата публикации статьи;
                                                            # для установки значения по умолчанию используеся функция Django now (возвращает текущие дату и время),
                                                            # можно рассматривать ее как стандартную функцию datetime.now из Python, но с учетом временной зоны ?
    created = models.DateTimeField(auto_now_add=True)   # время сосздания статьи; используем параметр auto_now_add, поэтому дата будет сохраняться автоматически при создании объекта
    updated = models.DateTimeField(auto_now=True)       # дата и время, указывающие на период, когда статья была отредактирована.
                                                        # Так как мы используем параметр auto_now, то дата будет сохраняться автоматически при сохранении объекта
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')   # статус статьи;
                                                                                        # параметр CHOICES используется, чтобы ограничить возможные значения из указанного списка
    objects = models.Manager()      # Менеджер по умолчанию
    published = PublishedManager()  # Собственный менеджер

    class Meta:                     # класс Meta внутри модели содержит метаданные
        ordering = ('-publish',)    # указали Django порядок сортировки статей (поле publish) по умолчанию – по убыванию даты публикации;
                                    # О том, что порядок убывающий, говорит префикс «-».
                                    # только что опубликованные статьи будут первыми в списке
       # db_table - этот атрибут позволяет изменить название таблицы в БД
    def __str__(self):      # возвращаем строковое отображение объекта; использует его во многих случаях, например на сайте администрирования
        return self.title

    def get_absolute_url(self):
        '''используется URL post_detail для построения канонического URL’а для объектов Post. 
        В Django есть соглашение о том, что метод модели get_absolute_url() должен возвращать 
        канонический URL объекта (имя этого метода применяется в HTML-шаблоне, чтобы получать ссылку на статью)'''
        # функцию reverse() дает возможность получать URL, указав имя URL-шаблона и его параметры (определены в urls.py)
        return reverse('blog:post_detail', 
                        args=[self.publish.year, self.publish.month, self.publish.day, self.slug])


class Comment(models.Model):
    '''Модель Comment содержит ForeignKey для привязки к определенной статье.
    Это отношение определено как «один ко многим»: одна статья может иметь множество комментариев,
    но каждый комментарий может быть оставлен только для одной статьи'''
    post = models.ForeignKey(Post,  
                             on_delete=models.CASCADE, 
                             related_name='comments' # Атрибут related_name позволяет получить доступ к комментариям конкретной статьи. 
                                                     # Теперь можно обращаться к статье из комментария, используя запись comment.post, 
                                                     # и к комментариям статьи при помощи post.comments.all(). 
                                                     # Если не опрелять related_name, то используется имя связанной модели с постфиксом _set 
                                                     # (например, comment_set)
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True) # поле created для сортировки комментариев в хронологическом порядке
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True) # булевое поле active, для того чтобы была возможность скрыть некоторые комментарии (например, содержащие оскорбления)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Комментарий {self.name} на статью {self.post}'
