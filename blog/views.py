from django.shortcuts import render, get_object_or_404
from .models import Post
'''вся логика приложения описывается здесь. 
Каждый обработчик получает HTTP-запрос, обрабатывает его и возвращает ответ'''

def post_list(request):
    '''запрашиваем из базы данных все опубликованные статьи
    с помощью собственного менеджера published'''
    posts = Post.published.all()
    return render(request, 'blog/post/list.html', {'posts': posts}) # функция render() формирует шаблон со списком статей.
                                                                    # Она принимает 1. объект запроса request,
                                                                    #               2. путь к шаблону
                                                                    #               3. переменные контекста для этого шаблона.
                                                                    # В ответ вернется объект HttpResponse со сформированным текстом (обычно это HTML-код).
                                                                    # Функция render() использует переданный контекст при формировании шаблона,
                                                                    # поэтому любая переменная контекста будет доступна в шаблоне.
                                                                    # Процессоры контекста – это вызываемые функции, которые добавляют в контекст переменные.

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
