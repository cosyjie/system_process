from django.urls import path, include
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'system_process'

urlpatterns = [
    path('list/<str:list_type>/', login_required(views.ProcessListView.as_view()), name='list'),
    path('detail/<str:list_type>/<int:pid>', login_required(views.DetailView.as_view()), name='detail'),
    path('action/<str:list_type>/<str:action>/<int:pid>', login_required(views.ActionView.as_view()), name='action')
]
