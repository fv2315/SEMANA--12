from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import AthleteProfile, membership_code_validator, phone_validator


def sanitize_input(value: str) -> str:
    return ' '.join(value.strip().split())


class AthleteRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        label='Nombre completo',
        max_length=120,
    )
    membership_code = forms.CharField(
        label='Código de socio',
        max_length=12,
        validators=[membership_code_validator],
        help_text='Formato: DEP-2026.',
    )
    email = forms.EmailField(label='Correo electrónico')
    phone = forms.CharField(
        label='Teléfono',
        max_length=16,
        validators=[phone_validator],
    )
    sport = forms.ChoiceField(
        label='Disciplina deportiva',
        choices=AthleteProfile.SPORT_CHOICES,
    )
    skill_level = forms.ChoiceField(
        label='Nivel deportivo',
        choices=AthleteProfile.LEVEL_CHOICES,
    )
    birth_date = forms.DateField(
        label='Fecha de nacimiento',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['username'].help_text = 'Elige un usuario para iniciar sesión.'
        self.order_fields(
            (
                'full_name',
                'membership_code',
                'email',
                'phone',
                'sport',
                'skill_level',
                'birth_date',
                'username',
                'password1',
                'password2',
            )
        )

    def clean_full_name(self):
        value = sanitize_input(self.cleaned_data['full_name'])
        if len(value) < 5:
            raise ValidationError('Ingrese su nombre y apellido.')
        return value

    def clean_membership_code(self):
        code = sanitize_input(self.cleaned_data['membership_code']).upper()
        if AthleteProfile.objects.filter(membership_code=code).exists():
            raise ValidationError('Este código de socio ya está registrado.')
        return code

    def clean_email(self):
        email = sanitize_input(self.cleaned_data['email']).lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este correo ya tiene una cuenta.')
        return email

    def clean_phone(self):
        return sanitize_input(self.cleaned_data['phone'])

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            self.add_error(
                'birth_date',
                'La fecha de nacimiento no puede ser futura.',
            )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            with transaction.atomic():
                user.save()
                AthleteProfile.objects.create(
                    user=user,
                    full_name=self.cleaned_data['full_name'],
                    membership_code=self.cleaned_data['membership_code'],
                    email=self.cleaned_data['email'],
                    phone=self.cleaned_data['phone'],
                    sport=self.cleaned_data['sport'],
                    skill_level=self.cleaned_data['skill_level'],
                    birth_date=self.cleaned_data['birth_date'],
                )
        return user


class ContactForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100)
    email = forms.EmailField(label='Correo electrónico')
    subject = forms.CharField(label='Asunto', max_length=150)
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'rows': 5}),
        max_length=1000,
    )

    def clean_name(self):
        name = sanitize_input(self.cleaned_data['name'])
        if len(name) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return name

    def clean_subject(self):
        subject = sanitize_input(self.cleaned_data['subject'])
        if subject.lower() in ('prueba', 'test'):
            raise ValidationError('Ingrese un asunto descriptivo.')
        return subject

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise ValidationError('El mensaje debe tener al menos 10 caracteres.')
        return message


class AthleteProfileForm(forms.ModelForm):
    class Meta:
        model = AthleteProfile
        fields = (
            'full_name',
            'membership_code',
            'email',
            'phone',
            'sport',
            'skill_level',
            'birth_date',
        )
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_full_name(self):
        return sanitize_input(self.cleaned_data['full_name'])

    def clean_email(self):
        email = sanitize_input(self.cleaned_data['email']).lower()
        if (
            AthleteProfile.objects
            .filter(email__iexact=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError('Este correo ya pertenece a otro perfil.')
        return email

    def clean_membership_code(self):
        return sanitize_input(self.cleaned_data['membership_code']).upper()

    def clean_phone(self):
        return sanitize_input(self.cleaned_data['phone'])
