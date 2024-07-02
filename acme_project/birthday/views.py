# Импортируем класс пагинатора.
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404, redirect

# Импортируем класс BirthdayForm, чтобы создать экземпляр формы.
from .forms import BirthdayForm, CongratulationForm

# Импортируем из utils.py функцию для подсчёта дней.
from .utils import calculate_birthday_countdown

# Импортируем модель дней рождения.
from .models import Birthday, Congratulation

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy, reverse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

class CongratulationCreateView(LoginRequiredMixin, CreateView):
    birthday = None
    model = Congratulation
    form_class = CongratulationForm

    # Переопределяем dispatch()
    def dispatch(self, request, *args, **kwargs):
        self.birthday = get_object_or_404(Birthday, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    # Переопределяем form_valid()
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.birthday = self.birthday
        return super().form_valid(form)

    # Переопределяем get_success_url()
    def get_success_url(self):
        return reverse('birthday:detail', kwargs={'pk': self.birthday.pk})

# Будут обработаны POST-запросы только от залогиненных пользователей.
# @login_required
# def add_comment(request, pk):
#     # Получаем объект дня рождения или выбрасываем 404 ошибку.
#     birthday = get_object_or_404(Birthday, pk=pk)
#     # Функция должна обрабатывать только POST-запросы.
#     form = CongratulationForm(request.POST)
#     if form.is_valid():
#         # Создаём объект поздравления, но не сохраняем его в БД.
#         congratulation = form.save(commit=False)
#         # В поле author передаём объект автора поздравления.
#         congratulation.author = request.user
#         # В поле birthday передаём объект дня рождения.
#         congratulation.birthday = birthday
#         # Сохраняем объект в БД.
#         congratulation.save()
#     # Перенаправляем пользователя назад, на страницу дня рождения.
#     return redirect('birthday:detail', pk=pk)

@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')

# Создаём миксин.
# Убрали миксин потому что отпала надобность в success_url так как создали
# в моделе функцию get_absolute_url для получения абсолютного урл для каждой записи
# а model = Birthday опять перенесли в классы
# class BirthdayMixin:
#     model = Birthday
#     success_url = reverse_lazy('birthday:list')

# Класс UserPassesTestMixin унаследован от AccessMixin,
# который по умолчанию переадресует анонимных пользователей на страницу логина.
# Поэтому при использовании UserPassesTestMixin миксин LoginRequiredMixin
# можно не использовать: он будет избыточным.

# Такую проверку надо разместить во всех CBV, где нужна проверка авторства.
# Выглядит громоздко: помимо того, что при объявлении CBV надо добавить
# миксин UserPassesTestMixin, в каждый класс придётся добавлять одно и то же
# описание метода test_func().
# В такой ситуации гораздо выгоднее написать собственный миксин,
# унаследованный от UserPassesTestMixin:
class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

# Наследуем класс от встроенного ListView:
class BirthdayListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Birthday
    # По умолчанию этот класс
    # выполняет запрос queryset = Birthday.objects.all(),
    # но мы его переопределим:
    queryset = Birthday.objects.prefetch_related(
        'tags'
    ).select_related('author')
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 10

class BirthdayCreateView(CreateView):
    model = Birthday
    form_class = BirthdayForm
    # # Указываем модель, с которой работает CBV...
    # model = Birthday
    # # Этот класс сам может создать форму на основе модели!
    # # Нет необходимости отдельно создавать форму через ModelForm.
    # # Указываем поля, которые должны быть в форме:
    # # используем готовую часть формы BirthdayForm с виджетами из формс
    # form_class = BirthdayForm
    # # Явным образом указываем шаблон:
    # template_name = 'birthday/birthday.html'
    # # Указываем namespace:name страницы, куда будет перенаправлен пользователь
    # # после создания объекта:
    # success_url = reverse_lazy('birthday:list')
    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form)



class BirthdayUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование записей"""
    model = Birthday
    form_class = BirthdayForm
    # model = Birthday
    # form_class = BirthdayForm
    # template_name = 'birthday/birthday.html'
    # success_url = reverse_lazy('birthday:list')

# def birthday_list(request):
#     # Получаем список всех объектов с сортировкой по id.
#     birthdays = Birthday.objects.order_by('id')
#     # Создаём объект пагинатора с количеством 10 записей на страницу.
#     paginator = Paginator(birthdays, 10)
#
#     # Получаем из запроса значение параметра page.
#     page_number = request.GET.get('page')
#     # Получаем запрошенную страницу пагинатора.
#     # Если параметра page нет в запросе или его значение не приводится к числу,
#     # вернётся первая страница.
#     page_obj = paginator.get_page(page_number)
#     # Вместо полного списка объектов передаём в контекст
#     # объект страницы пагинатора
#
#     # Передаём их в контекст шаблона.
#     context = {'page_obj': page_obj}
#     return render(request, 'birthday/birthday_list.html', context)

# Добавим опциональный параметр pk.
# def birthday(request, pk=None):
#     # Если в запросе указан pk (если получен запрос на редактирование объекта):
#     if pk is not None:
#         # Получаем объект модели или выбрасываем 404 ошибку.
#         instance = get_object_or_404(Birthday, pk=pk)
#     # Если в запросе не указан pk
#     # (если получен запрос к странице создания записи):
#     else:
#         # Связывать форму с объектом не нужно, установим значение None.
#         instance = None
#     # Передаём в форму либо данные из запроса, либо None.
#     # В случае редактирования прикрепляем объект модели.
#
#     # Этот код гораздо короче, а работает точно так же, как и предыдущий вариант.
#     # Весь фокус в выражении BirthdayForm(request.GET or None).
#     # Его логика такова: если в GET-запросе были переданы параметры — значит,
#     # объект request.GET не пуст и этот объект передаётся в форму;
#     # если же объект request.GET пуст — срабатывает условиe or и форма
#     # создаётся без параметров, через BirthdayForm(None) — это идентично
#     # обычному BirthdayForm().
#     form = BirthdayForm(
#         request.POST or None,
#         # Файлы, переданные в запросе, указываются отдельно.
#         files=request.FILES or None,
#         instance=instance
#     )
#     # Создаём словарь контекста сразу после инициализации формы.
#     context = {'form': form}
#     # Если форма валидна...
#     if form.is_valid():
#         # В классе ModelForm есть встроенный метод save(),
#         # он позволяет сохранить данные из формы в БД.
#         # После сохранения метод save() возвращает сохранённый
#         # объект — это можно использовать для подтверждения,
#         # что сохранение данных прошло успешно.
#         # Добавим строчку с вызовом метода save():
#         form.save()
#         # ...вызовем функцию подсчёта дней:
#         birthday_countdown = calculate_birthday_countdown(
#             # ...и передаём в неё дату из словаря cleaned_data.
#             form.cleaned_data['birthday']
#         )
#         # Обновляем словарь контекста: добавляем в него новый элемент.
#         context.update({'birthday_countdown': birthday_countdown})
#     return render(request, 'birthday/birthday.html', context)

class BirthdayDeleteView(OnlyAuthorMixin, DeleteView):
    model = Birthday

# def delete_birthday(request, pk):
#     # Получаем объект модели или выбрасываем 404 ошибку.
#     instance = get_object_or_404(Birthday, pk=pk)
#     # В форму передаём только объект модели;
#     # передавать в форму параметры запроса не нужно.
#     form = BirthdayForm(instance=instance)
#     context = {'form': form}
#     # Если был получен POST-запрос...
#     if request.method == 'POST':
#         # ...удаляем объект:
#         instance.delete()
#         # ...и переадресовываем пользователя на страницу со списком записей.
#         return redirect('birthday:list')
#     # Если был получен GET-запрос — отображаем форму.
#     return render(request, 'birthday/birthday.html', context)

class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context


