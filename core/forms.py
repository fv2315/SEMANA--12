from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import StudentProfile


code_validator = RegexValidator(
    regex=r'^202\d{4,7}$',
    message='El código debe comenzar con 202 y contener entre 7 y 10 dígitos.',
)


class StudentRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=120)
    code = forms.CharField(max_length=12, validators=[code_validator])
    email = forms.EmailField()
    phone = forms.CharField(max_length=16)
    career = forms.ChoiceField(choices=StudentProfile.CAREER_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_full_name(self):
        value = self.cleaned_data['full_name'].strip()
        if len(value) < 5:
            raise ValidationError('Ingrese nombre y apellidos completos.')
        return ' '.join(value.split())

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if StudentProfile.objects.filter(code=code).exists():
            raise ValidationError('Este código ya está registrado.')
        return code.upper()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        full_name = cleaned_data.get('full_name')
        if username and full_name and username.lower() in full_name.lower():
            self.add_error(
                'username',
                'El nombre de usuario no debe aparecer en el nombre completo.',
            )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            StudentProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                code=self.cleaned_data['code'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'].strip(),
                career=self.cleaned_data['career'],
            )
        return user


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=150)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        max_length=1000,
    )

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return ' '.join(name.split())

    def clean_subject(self):
        subject = self.cleaned_data['subject'].strip()
        if subject.lower() in ('prueba', 'test'):
            raise ValidationError('Use un asunto descriptivo.')
        return subject

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 10:
            raise ValidationError('El mensaje debe ser más descriptivo.')
        return message


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('full_name', 'code', 'email', 'phone', 'career')

    def clean_full_name(self):
        value = self.cleaned_data['full_name'].strip()
        return ' '.join(value.split()).title()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if (
            StudentProfile.objects
            .filter(email=email)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ValidationError('Este correo ya está registrado.')
        return email
