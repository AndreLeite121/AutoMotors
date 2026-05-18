
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'garagem'

urlpatterns = [
    path('', views.index,name='index'),
    path('adicionar/', views.adc,name='adicionar'),
    path('detalhes/<int:pk>',views.detalhes,name="detalhes"),
    path('all/', views.indexall,name='all'), 
    path('add_review/', views.add_review, name='add_review'),
 
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
