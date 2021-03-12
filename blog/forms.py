'''В Django встроены два базовых класса форм:
1.  Form – позволяет создавать стандартные формы;
2.  ModelForm– дает возможность создавать формы по объектам моделей.

Формы могут быть описаны в любом месте проекта, 
но есть общее соглашение, чтобы они находились в файле forms.py каждого приложения
'''
from django import forms

class EmailPostForm(forms.Form):
    '''каждый тип по умолчанию имеет виджет для отображения в HTML. Виджет может быть изменен с помощью параметра widget.
    Валидация поля зависит от его типа; нарушение формата выбрасывает исключение forms.ValidationError'''
    name = forms.CharField(max_length=25) # это поле будет отображаться как элемент <inputtype="text">
    email = forms.EmailField() # получать только корректные e-mail-адреса
    to = forms.EmailField()    # получать только корректные e-mail-адреса
    comments = forms.CharField(required=False, widget=forms.Textarea) # required=False делает поле необязательным;
                                                                      # используем виджет Textarea для отображения HTML-элемента <text area> вместо стандартного <input>

