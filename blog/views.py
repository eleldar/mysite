'''вся логика приложения описывается здесь. 
Каждый обработчик получает HTTP-запрос, обрабатывает его и возвращает ответ

И спользование обработчиков - классов
Использование класса – это альтернативный способ реализации обработчи-
ков. Так как обработчик – это вызываемая функция, которая принимает запрос
и возвращает ответ, мы можем реализовать его в виде метода класса. Django
предоставляет для этого базовый класс обработчиков. Все они должны быть
унаследованы от класса View, который управляет вызовом нужного метода в за-
висимости от HTTP-запроса и некоторыми другими функциями.
Обработчики-классы в некоторых случаях могут быть более полезными, чем
функции-обработчики. Их преимущества заключаются в следующем:
  группируют код в несколько функций в зависимости от HTTP-методов
запроса, таких как GET,POST, PUT;
  позволяют задействовать множественное наследование для создания
многократно используемых обработчиков (их часто называют примеся-
ми, или миксинами).
'''
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count # функция агрегации Count из Django;
                                   # позволяет выполнять агрегирующий запрос
                                   # для подсчета количества тегов на уровне
                                   # базы данных. Cодержит еще функции:
                                   #  Avg – среднее значение;
                                   #  Max – максимальное значение;
                                   #  Min – минимальное значение;
                                   #  Count – количество объектов.
from django.contrib.postgres.search import SearchVector # класс для полнотекстового поиска по нескольким полям
from django.contrib.postgres.search import SearchQuery, SearchRank # Класс SearchQuery предназначен для преобразования фраз в объект поискового запроса;
                                                                   # по умолчанию все фразы пропускаются через алгоритм стемминга, который помогает получить больше совпадений.
                                                                   # Класс SearchRank сортирует результаты на основе того, как часто встречаются фразы поиска и как близко друг к другу они находятся
from django.contrib.postgres.search import TrigramSimilarity # для поиска текста по сходству триграмм;
                                                             # Чтобы использовать триграммы в PostgerSQL, необходимо подключить расширение pg_trgm;
                                                             # Требовалось выполнить команду для входа в консоль PostgreSQL: "psql blog";
                                                             # затем установить расширение pg_trgm, выполнив следующую команду: "CREATE EXTENSION pg_trgm;"

def post_list(request, tag_slug=None): # Принимаем необязательный аргумент tag_slug, который по умолчанию равен None.
                                       # Этот параметр будет задаваться в URL’е
    object_list = Post.published.all() # используем переопределенный QuerySet модели вместо получения всех объектов;
                                       # находим все опубликованные статьи
    tag = None

    if tag_slug: # если указан слаг тега, получаем соответствующий объект модели Tag с помощью метода get_object_or_404()
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag]) # фильтруем изначальный список статей и оставляем только те,
                                                         # которые связаны с полученным тегом.
                                                         # Так как это связь «многие ко многим», необходимо фильтровать статьи
                                                         # по вхождению тегов в список тегов

    paginator = Paginator(object_list, 3) # по 3 статьи на странице
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger: # Страница не является целым числом; присвиваем 1
        posts = paginator.page(1)
    except EmptyPage: # Выход за пределы интервала; присвиваем последнюю страницу
        posts = paginator.page(paginator.num_pages)

    context = {'page': page, 'posts': posts, 'tag': tag}
    return render (request, 'blog/post/list.html', context=context)


def post_detail(request, year, month, day, post): 
    '''принимает аргументы для получения статьи по указанным слагу и дате,
    чтобы гарантированно получить статью по комбинации этих полей,
    поскольку слаг должен быть уникальным для статей, созданных в один день'''
    post = get_object_or_404(Post, # используем get_object_or_404() для поиска нужной статьи;
                                   # возвращает объект, который подходит по указанным параметрам,
                                   # или вызывает исключение HTTP 404 (объект не найден), если не найдет ни одной статьи
                             slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # Список активных комментариев для этой статьи
    comments = post.comments.filter(active=True) # добавили QuerySet для получения всех активных комментариев,
                                                 # используя объект статьи post и менеджер связанных объектов comments, 
                                                 # определенный в модели Comment в аргументе related_name.
    new_comment = None # используется, когда новый комментарий будет успешно создан
    if request.method == 'POST':
        # Пользователь отправил комментарий
        comment_form = CommentForm(data=request.POST) # Если получаем POST-запрос, то заполняем форму данными из запроса
        if comment_form.is_valid(): # валидируем POST-запрос методом is_valid(); при некорректном заполнении
                                    # отображаем HTML-шаблон с сообщениями об ошибках
            # Создаем комментарий, но пока не сохраняем в базе данных
            new_comment = comment_form.save(commit=False) # создаем новый объект Comment с помощью метода save;
                                                          # save() создает объект модели, с которой связана форма, и сохраняет его в базу данных. 
                                                          # Если в качестве аргумента метода передать commit=False, то объект будет создан, 
                                                          # но не будет сохранен в базу данных, чтобы изменить данные перед сохранением объекта  
                                                          # Метод save() доступен для ModelForm, но не дляForm, т.к. последние не привязываются к моделям
            # Привязываем статью к комментарию
            new_comment.post = post # указываем в комментарии ссылку на объект статьи
            # Сохраняем комментарий в базе данных
            new_comment.save() # сохраняем комментарий в базу данных
    else:
        comment_form = CommentForm() # используем для инициализации формы при GET-запросе
    # Формирование списка похожих статей
    post_tags_ids = post.tags.values_list('id', flat=True) # получает все ID тегов текущей статьи;
                                                           # Метод QuerySet’а values_list() возвращает кортежи со значениями заданного поля. 
                                                           # Мы указали flat=True, чтобы получить «плоский» список вида [1, 2, 3, ...]
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id) # получает все статьи, содержащие хоть один тег из полученных ранее, исключая текущую статью;
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4] # использует функцию агрегации Count 
                                                           # для формирования вычисляемого поля same_tags, 
                                                           # которое содержит определенное количество совпадающих тегов;
                                                           # сортирует список опубликованных статей в убывающем порядке по количеству 
                                                           # совпадающих тегов для отображения первыми максимально похожих статей и 
                                                           # делает срез результата для отображения только четырех статей.
    context = {'post': post, 'comments': comments, 'new_comment': new_comment,
               'comment_form': comment_form, 'similar_posts': similar_posts}
    return render(request, 'blog/post/detail.html', context=context)

def post_share(request, post_id):
    '''получение статьи по идентификатору'''
    post = get_object_or_404(Post, id=post_id, status='published') # получения статьи с указанным идентификатором; убеждаемся, что статья опубликована; иначе - 404
    '''Для разделения логики отображения формы или ее обработки используется запрос request. 
       Заполненная форма отправляется методом POST. Если метод запроса – GET, необходимо отобразить 
       пустую форму; если приходит запрос POST, обрабатываем данные формы и отправляем их на почту.'''
    sent = False # объявили переменную sent, она будет установлена в True после отправки сообщения
                 # Будем использовать эту переменную позже для отображения сообщения об успешной отправке в HTML-шаблоне.
    if request.method == 'POST':
        # отправка формы на сохранение
        form = EmailPostForm(request.POST) # Cоздаем объект формы, используя полученые из request.POST данные
        if form.is_valid(): # проверка введенных данных; возвращает True, если ошибок не найдено. 
                            # если хотя бы одно поле содержит неверное значение, возвращается False.
                            # Если форма некорректна, то возвращаем ее с введенными пользователем 
                            # данными и сообщениями об ошибках (требуется позже добавить в HTML-шаблон).
            cd = form.cleaned_data # получаем введенные данные с помощью form.cleaned_data. 
                                   # Этот атрибут является словарем с полями формы и их значениями.
                                   # Если форма не проходит валидацию, то в атрибут cleaned_data попадут только корректные поля.
            #Отправка электронной почты
            post_url = request.build_absolute_uri(post.get_absolute_url()) # используем метод объекта запроса request.build_absolute_uri(),
                                                                           # чтобы добавить в сообщение абсолютную ссылку (Полученная абсолютная ссылка будет содержать HTTP-схему и имя хоста);
                                                                           # в request.build_absolute_uri() передается результат выполнения get_absolute_url()
            subject = f"{cd['name']} ({cd['email']}) рекомендует Вам прочитать статью {post.title}"              # тема сообщения
            message = f"Для чтения статьи: {post.title} \n\nперейдите по ссылке: {post_url}\n\nкомментарий {cd['name']}: {cd['comments']}" # текст сообщения
            send_mail(subject, message, 'admin', [cd['to']]) # Функция send_mail() принимает в качестве обязательных аргументов тему, сообщение, отправителя и список получателей. 
                                                             # Указав дополнительный параметр fail_silently=False, мы говорим, чтобы при сбое в отправке сообщения было сгенерировано исключение. 
                                                             # Если в результате выполнения вы увидите 1, ваше письмо успешно отправлено.
                                                             # В данном случае отправили e-mail по адресам, указанным в поле to формы.
            sent = True
    else:
        form = EmailPostForm() # Когда обработчик выполняется первый раз с GET-запросом, 
                               # создается объект form, который будет отображен в шаблоне как пустая форма;
                               # Пользователь заполняет форму и отправляет POST-запросом.
    context = {'post': post, 'form': form, 'sent': sent}
    return render(request, 'blog/post/share.html', context=context)


def post_search(request):
    form = SearchForm() # создаем объект формы SearchForm
    query = None
    results = []
    if 'query' in request.GET: # Поисковый запрос будет отправляться методом GET, чтобы результирующий URL содержал в себе фразу поиска в параметре query.
                               # Для того чтобы определить, отправлена ли форма для поиска, обращаемся к параметру запроса query из словаря request.GET
        form = SearchForm(request.GET) # Когда запрос отправлен, мы инициализируем объект формы с параметрами из request.GET, 
        if form.is_valid(): # проверяем корректность введенных данных
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B') # формируем запрос c разным весом для полей: title и body;
                                                                                                 # По умолчанию используются веса D, C, B и A, которые соответствуют числам 0.1, 0.2, 0.4 и 1. 
                                                                                                 # для вектора по полю title применили вес 1.0, для вектора по полю body - 0.4.
            search_query = SearchQuery(query)
            results = Post.objects.annotate(similarity=TrigramSimilarity('title', query)).filter(similarity__gt=0.3).order_by('-similarity')

    context = {'form': form, 'query': query, 'results': results}
    return render(request, 'blog/post/search.html', context=context)

