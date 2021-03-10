'''вся логика приложения описывается здесь. 
Каждый обработчик получает HTTP-запрос, обрабатывает его и возвращает ответ'''
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
    '''запрашиваем из базы данных все опубликованные статьи
    с помощью собственного менеджера published'''
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3) # инициализируем объект класса Paginator, указав количество объектов на одной странице
    page = request.GET.get('page') # извлекаем из запроса GET-параметр page, который указывает текущую страницу
    try:
        posts = paginator.page(page) # получаем список объектов на нужной странице с помощью метода page() класса Paginator
    except PageNotAnInteger:
        posts = paginator.page(1) # если указанный параметр page не является целым числом, обращаемся к первой странице
    except EmptyPage:
        posts = paginator.page(paginator.num_pages) # если page больше, чем общее количество страниц, то возвращаем последнюю
    context = {'page': page, 'posts': posts} # передаем номер страницы и полученные объекты в шаблон
    return render(request, 'blog/post/list.html', context=context) 

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
    return render(request, 'blog/post/detail.html', {'post': post})
