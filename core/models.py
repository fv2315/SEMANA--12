from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message='Ingrese un teléfono válido con 7 a 15 dígitos.',
)


class StudentProfile(models.Model):
    CAREER_CHOICES = (
        ('sistemas', 'Ingeniería de Sistemas'),
        ('industrial', 'Ingeniería Industrial'),
        ('mecanica', 'Ingeniería Mecánica'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
    )
    full_name = models.CharField(max_length=120)
    code = models.CharField(max_length=12, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=16, validators=[phone_validator])
    career = models.CharField(max_length=20, choices=CAREER_CHOICES)
    is_active_record = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Perfil de estudiante'
        verbose_name_plural = 'Perfiles de estudiantes'

    def __str__(self):
        return f'{self.full_name} ({self.code})'

    @property
    def display_name(self):
        return self.full_name.title()
