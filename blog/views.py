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
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail

class PostListView(ListView):
    '''Заменили функцию post_list на класс-наследник ListView Django. 
    Этот базовый класс обработчика списков позволяет отображать несколько объектов любого типа.'''
    queryset = Post.published.all() # используем переопределенный QuerySet модели вместо
                                    # получения всех объектов.
                                    # Вместо задания атрибута QuerySet мы могли бы указать
                                    # модель model=Post, и тогда Django, используя 
                                    # стандартный менеджер модели, получал бы объекты как 
                                    # Post.objects.all()
    context_object_name = 'posts'   # используем posts в качестве переменной контекста 
                                    # HTML-шаблона, в которой будет храниться список объектов. 
                                    # Если не указать атрибут context_object_name, то
                                    # по умолчанию будет использоваться переменная object_list,
                                    # т.е. ей нужно будет передавать данные для отображения
                                    # на HTML-странице
    paginate_by = 3 # используем постраничное отображение по три объекта на странице
    template_name = 'blog/post/list.html' # используем указанный шаблон для формирования 
                                          # страницы; если не указать template_name, 
                                          # то базовый класс ListView искал бы
                                          # шаблон blog/post_list.html

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
    context = {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form}
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
