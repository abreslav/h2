from django.urls import path
from . import views

app_name = 'django_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_with_llm, name='chat_with_llm'),
]