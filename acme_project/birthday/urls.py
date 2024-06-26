from django.urls import path

from . import views

app_name = 'birthday'

urlpatterns = [
    path('', views.BirthdayCreateView.as_view(), name='create'),
    # Новый маршрут.
    path('list/', views.BirthdayListView.as_view(), name='list'),
    # новый маршрут для формы отображения подсчета дней.
    path('<int:pk>/', views.BirthdayDetailView.as_view(), name='detail'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    # Маршрут для редактирования.
    path('<int:pk>/edit/', views.BirthdayUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.BirthdayDeleteView.as_view(), name='delete'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('login_only/', views.simple_view),
]
