import re

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def migrate_sports_and_codes(apps, schema_editor):
    AthleteProfile = apps.get_model('core', 'AthleteProfile')
    athletes = list(AthleteProfile.objects.order_by('pk'))
    sports = {
        'sistemas': 'futbol',
        'industrial': 'basquetbol',
        'mecanica': 'natacion',
    }
    used_codes = {
        athlete.membership_code
        for athlete in athletes
        if re.fullmatch(r'DEP-\d{4,8}', str(athlete.membership_code))
    }

    for athlete in athletes:
        legacy_code = str(athlete.membership_code)
        if not re.fullmatch(r'DEP-\d{4,8}', legacy_code):
            digits = ''.join(char for char in legacy_code if char.isdigit())
            digits = (
                digits[-8:]
                if len(digits) >= 4
                else f'{athlete.pk:08d}'[-8:]
            )
            candidate = f'DEP-{digits}'
            sequence = athlete.pk
            while candidate in used_codes:
                candidate = f'DEP-{sequence % 100_000_000:08d}'
                sequence += 1
            athlete.membership_code = candidate
            used_codes.add(candidate)
        athlete.sport = sports.get(athlete.sport, 'futbol')
        athlete.save(update_fields=('membership_code', 'sport'))


def reverse_sports_and_codes(apps, schema_editor):
    AthleteProfile = apps.get_model('core', 'AthleteProfile')
    sports = {
        'futbol': 'sistemas',
        'basquetbol': 'industrial',
        'natacion': 'mecanica',
    }

    for athlete in AthleteProfile.objects.all().iterator():
        if athlete.membership_code.startswith('DEP-'):
            athlete.membership_code = athlete.membership_code[4:]
        athlete.sport = sports.get(athlete.sport, 'sistemas')
        athlete.save(update_fields=('membership_code', 'sport'))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StudentProfile',
            new_name='AthleteProfile',
        ),
        migrations.RenameField(
            model_name='athleteprofile',
            old_name='code',
            new_name='membership_code',
        ),
        migrations.RenameField(
            model_name='athleteprofile',
            old_name='career',
            new_name='sport',
        ),
        migrations.RenameField(
            model_name='athleteprofile',
            old_name='is_active_record',
            new_name='is_active',
        ),
        migrations.RunPython(
            migrate_sports_and_codes,
            reverse_sports_and_codes,
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='membership_code',
            field=models.CharField(
                max_length=12,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Use el formato DEP- seguido de 4 a 8 dígitos.',
                        regex='^DEP-\\d{4,8}$',
                        flags=re.IGNORECASE,
                    ),
                ],
                verbose_name='código de socio',
            ),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='sport',
            field=models.CharField(
                choices=[
                    ('futbol', 'Fútbol'),
                    ('basquetbol', 'Básquetbol'),
                    ('voleibol', 'Vóleibol'),
                    ('natacion', 'Natación'),
                    ('atletismo', 'Atletismo'),
                    ('artes_marciales', 'Artes marciales'),
                ],
                max_length=20,
                verbose_name='disciplina',
            ),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='athlete_profile',
                to='auth.user',
            ),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='full_name',
            field=models.CharField(max_length=120, verbose_name='nombre completo'),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='correo electrónico'),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='phone',
            field=models.CharField(
                max_length=16,
                validators=[
                    django.core.validators.RegexValidator(
                        message='Ingrese un teléfono válido con 7 a 15 dígitos.',
                        regex='^\\+?[0-9]{7,15}$',
                    ),
                ],
                verbose_name='teléfono',
            ),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='membresía activa'),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                verbose_name='fecha de registro',
            ),
        ),
        migrations.AlterField(
            model_name='athleteprofile',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='última actualización',
            ),
        ),
        migrations.AddField(
            model_name='athleteprofile',
            name='skill_level',
            field=models.CharField(
                choices=[
                    ('principiante', 'Principiante'),
                    ('intermedio', 'Intermedio'),
                    ('avanzado', 'Avanzado'),
                ],
                default='principiante',
                max_length=20,
                verbose_name='nivel deportivo',
            ),
        ),
        migrations.AddField(
            model_name='athleteprofile',
            name='birth_date',
            field=models.DateField(
                blank=True,
                null=True,
                verbose_name='fecha de nacimiento',
            ),
        ),
        migrations.AlterModelOptions(
            name='athleteprofile',
            options={
                'ordering': ('-created_at',),
                'verbose_name': 'deportista',
                'verbose_name_plural': 'deportistas',
            },
        ),
    ]
