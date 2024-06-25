# Импортируем класс пагинатора.
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404, redirect

# Импортируем класс BirthdayForm, чтобы создать экземпляр формы.
from .forms import BirthdayForm

# Импортируем из utils.py функцию для подсчёта дней.
from .utils import calculate_birthday_countdown

# Импортируем модель дней рождения.
from .models import Birthday

from django.views.generic import ListView

def birthday_list(request):
    # Получаем список всех объектов с сортировкой по id.
    birthdays = Birthday.objects.order_by('id')
    # Создаём объект пагинатора с количеством 10 записей на страницу.
    paginator = Paginator(birthdays, 10)

    # Получаем из запроса значение параметра page.
    page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора.
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
    page_obj = paginator.get_page(page_number)
    # Вместо полного списка объектов передаём в контекст
    # объект страницы пагинатора

    # Передаём их в контекст шаблона.
    context = {'page_obj': page_obj}
    return render(request, 'birthday/birthday_list.html', context)

# Добавим опциональный параметр pk.
def birthday(request, pk=None):
    # Если в запросе указан pk (если получен запрос на редактирование объекта):
    if pk is not None:
        # Получаем объект модели или выбрасываем 404 ошибку.
        instance = get_object_or_404(Birthday, pk=pk)
    # Если в запросе не указан pk
    # (если получен запрос к странице создания записи):
    else:
        # Связывать форму с объектом не нужно, установим значение None.
        instance = None
    # Передаём в форму либо данные из запроса, либо None.
    # В случае редактирования прикрепляем объект модели.

    # Этот код гораздо короче, а работает точно так же, как и предыдущий вариант.
    # Весь фокус в выражении BirthdayForm(request.GET or None).
    # Его логика такова: если в GET-запросе были переданы параметры — значит,
    # объект request.GET не пуст и этот объект передаётся в форму;
    # если же объект request.GET пуст — срабатывает условиe or и форма
    # создаётся без параметров, через BirthdayForm(None) — это идентично
    # обычному BirthdayForm().
    form = BirthdayForm(
        request.POST or None,
        # Файлы, переданные в запросе, указываются отдельно.
        files=request.FILES or None,
        instance=instance
    )
    # Создаём словарь контекста сразу после инициализации формы.
    context = {'form': form}
    # Если форма валидна...
    if form.is_valid():
        # В классе ModelForm есть встроенный метод save(),
        # он позволяет сохранить данные из формы в БД.
        # После сохранения метод save() возвращает сохранённый
        # объект — это можно использовать для подтверждения,
        # что сохранение данных прошло успешно.
        # Добавим строчку с вызовом метода save():
        form.save()
        # ...вызовем функцию подсчёта дней:
        birthday_countdown = calculate_birthday_countdown(
            # ...и передаём в неё дату из словаря cleaned_data.
            form.cleaned_data['birthday']
        )
        # Обновляем словарь контекста: добавляем в него новый элемент.
        context.update({'birthday_countdown': birthday_countdown})
    return render(request, 'birthday/birthday.html', context)

def delete_birthday(request, pk):
    # Получаем объект модели или выбрасываем 404 ошибку.
    instance = get_object_or_404(Birthday, pk=pk)
    # В форму передаём только объект модели;
    # передавать в форму параметры запроса не нужно.
    form = BirthdayForm(instance=instance)
    context = {'form': form}
    # Если был получен POST-запрос...
    if request.method == 'POST':
        # ...удаляем объект:
        instance.delete()
        # ...и переадресовываем пользователя на страницу со списком записей.
        return redirect('birthday:list')
    # Если был получен GET-запрос — отображаем форму.
    return render(request, 'birthday/birthday.html', context)
