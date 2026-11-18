from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from .forms import (
    AthleteProfileForm,
    AthleteRegistrationForm,
    ContactForm,
)
from .models import AthleteProfile


def home(request):
    context = {
        'athlete_count': AthleteProfile.objects.filter(is_active=True).count(),
        'sport_count': AthleteProfile.objects.filter(
            is_active=True,
        ).values('sport').distinct().count(),
    }
    return render(request, 'core/home.html', context)


def register(request):
    if request.method == 'POST':
        form = AthleteRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Tu cuenta deportiva está lista. ¡Bienvenido/a al equipo!',
            )
            return redirect('dashboard')
    else:
        form = AthleteRegistrationForm()
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


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('home')


@login_required
def dashboard(request):
    profile = getattr(request.user, 'athlete_profile', None)
    return render(request, 'core/dashboard.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile = getattr(request.user, 'athlete_profile', None)
    if profile is None:
        messages.warning(request, 'Primero complete su perfil.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AthleteProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('dashboard')
    else:
        form = AthleteProfileForm(instance=profile)
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


class AthleteListView(PermissionRequiredMixin, ListView):
    permission_required = 'core.view_athleteprofile'
    raise_exception = True
    model = AthleteProfile
    template_name = 'core/athlete_list.html'
    context_object_name = 'athletes'
    paginate_by = 20
