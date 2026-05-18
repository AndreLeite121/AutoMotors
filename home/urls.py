from django.urls import path
from django.views.generic import TemplateView
from . import views
from .decorators import http_only

app_name = 'home'


def public_template(template_name):
    """Atalho: TemplateView público envolvido em @http_only."""
    return http_only(TemplateView.as_view(template_name=template_name))


urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('meu-historico/', views.meu_historico_view, name='meu_historico'),
    path('add_review/', views.add_review, name='add_review'),
    path('termos-e-condicoes/',
         public_template('home/termos_e_condicoes.html'),
         name='termos_e_condicoes'),
    path('politica-de-privacidade/',
         public_template('home/politica_de_privacidade.html'),
         name='politica_de_privacidade'),
    path('central-de-ajuda/',
         public_template('home/central_de_ajuda.html'),
         name='central_de_ajuda'),
]
