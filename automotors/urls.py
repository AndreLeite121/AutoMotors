# automotors/urls.py — AutoMotors
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

from home.decorators import ssl_required


# Wrappers HTTPS-only para as views nativas do django.contrib.auth.
# Sem isso, /accounts/login/ aceitaria senha em HTTP puro.
auth_https_patterns = [
    path('login/',
         ssl_required(auth_views.LoginView.as_view()),
         name='login'),
    # Logout não transmite credenciais — só destrói a sessão. Mantemos sem
    # ssl_required para o form do navbar (em HTTP) postar same-origin e não
    # cair em "Origin: null" no CSRF check do Django.
    path('logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),
    path('password_change/',
         ssl_required(auth_views.PasswordChangeView.as_view()),
         name='password_change'),
    path('password_change/done/',
         ssl_required(auth_views.PasswordChangeDoneView.as_view()),
         name='password_change_done'),
    path('password_reset/',
         ssl_required(auth_views.PasswordResetView.as_view()),
         name='password_reset'),
    path('password_reset/done/',
         ssl_required(auth_views.PasswordResetDoneView.as_view()),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         ssl_required(auth_views.PasswordResetConfirmView.as_view()),
         name='password_reset_confirm'),
    path('reset/done/',
         ssl_required(auth_views.PasswordResetCompleteView.as_view()),
         name='password_reset_complete'),
]


# /admin/ inteiro fica em HTTPS — credenciais administrativas são sempre sensíveis.
admin.site.login = ssl_required(admin.site.login)
admin.site.logout = ssl_required(admin.site.logout)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('garagem/', include('garagem.urls')),
    path('acessorios/', include('acessorios.urls')),
    path('interesse/', include('cart.urls', namespace='cart')),
    path('accounts/', include(auth_https_patterns)),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
