from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.generic import ListView

from .forms import (
    ContactForm,
    StudentProfileForm,
    StudentRegistrationForm,
)
from .models import StudentProfile


def home(request):
    return render(request, 'core/home.html')


def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro completado. Sesión iniciada correctamente.')
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Bienvenido/a.')
            return redirect('dashboard')
    else:
        form = AuthenticationForm(request)
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('home')


@login_required
def dashboard(request):
    profile = getattr(request.user, 'student_profile', None)
    return render(request, 'core/dashboard.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = getattr(request.user, 'student_profile', None)
    if profile is None:
        messages.warning(request, 'Primero complete su perfil.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('dashboard')
    else:
        form = StudentProfileForm(instance=profile)
    return render(request, 'core/profile.html', {'form': form})


@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Mensaje recibido. Gracias por contactarnos.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


class StudentListView(PermissionRequiredMixin, ListView):
    permission_required = 'core.view_studentprofile'
    raise_exception = True
    model = StudentProfile
    template_name = 'core/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
