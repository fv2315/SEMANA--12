import re

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


phone_validator = RegexValidator(
    regex=r'^\+?[0-9]{7,15}$',
    message='Ingrese un teléfono válido con 7 a 15 dígitos.',
)
membership_code_validator = RegexValidator(
    regex=r'^DEP-\d{4,8}$',
    message='Use el formato DEP- seguido de 4 a 8 dígitos.',
    flags=re.IGNORECASE,
)


class AthleteProfile(models.Model):
    SPORT_CHOICES = (
        ('futbol', 'Fútbol'),
        ('basquetbol', 'Básquetbol'),
        ('voleibol', 'Vóleibol'),
        ('natacion', 'Natación'),
        ('atletismo', 'Atletismo'),
        ('artes_marciales', 'Artes marciales'),
    )
    LEVEL_CHOICES = (
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='athlete_profile',
    )
    full_name = models.CharField('nombre completo', max_length=120)
    membership_code = models.CharField(
        'código de socio',
        max_length=12,
        unique=True,
        validators=[membership_code_validator],
    )
    email = models.EmailField('correo electrónico')
    phone = models.CharField(
        'teléfono',
        max_length=16,
        validators=[phone_validator],
    )
    sport = models.CharField('disciplina', max_length=20, choices=SPORT_CHOICES)
    skill_level = models.CharField(
        'nivel deportivo',
        max_length=20,
        choices=LEVEL_CHOICES,
        default='principiante',
    )
    birth_date = models.DateField('fecha de nacimiento', blank=True, null=True)
    is_active = models.BooleanField('membresía activa', default=True)
    created_at = models.DateTimeField('fecha de registro', auto_now_add=True)
    updated_at = models.DateTimeField('última actualización', auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'deportista'
        verbose_name_plural = 'deportistas'

    def __str__(self):
        return f'{self.full_name} ({self.membership_code})'

    @property
    def display_name(self):
        return self.full_name.title()
