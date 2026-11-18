from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('panel/', views.dashboard, name='dashboard'),
    path('perfil/editar/', views.edit_profile, name='edit_profile'),
    path('contacto/', views.contact, name='contact'),
    path(
        'estudiantes/',
        views.StudentListView.as_view(),
        name='student_list',
    ),
]
