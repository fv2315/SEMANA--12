from datetime import date, timedelta

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .forms import AthleteRegistrationForm, ContactForm
from .models import AthleteProfile


class ValidationTests(TestCase):
    def test_contact_form_rejects_short_message(self):
        form = ContactForm(
            data={
                'name': 'Ana',
                'email': 'ana@example.com',
                'subject': 'Consulta',
                'message': 'hola',
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_registration_sanitizes_fields_and_creates_athlete(self):
        form = AthleteRegistrationForm(
            data={
                'username': 'ana_fit',
                'email': 'ANA@Example.COM',
                'password1': 'ClaveSegura-2026',
                'password2': 'ClaveSegura-2026',
                'full_name': '  Ana   Pérez López ',
                'membership_code': 'dep-2026001',
                'phone': '987654321',
                'sport': 'futbol',
                'skill_level': 'principiante',
                'birth_date': '',
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['full_name'], 'Ana Pérez López')
        self.assertEqual(form.cleaned_data['email'], 'ana@example.com')
        user = form.save()
        athlete = AthleteProfile.objects.get(user=user)
        self.assertEqual(athlete.membership_code, 'DEP-2026001')
        self.assertEqual(athlete.sport, 'futbol')

    def test_registration_rejects_future_birth_date(self):
        form = AthleteRegistrationForm(
            data={
                'username': 'future_athlete',
                'email': 'future@example.com',
                'password1': 'ClaveSegura-2026',
                'password2': 'ClaveSegura-2026',
                'full_name': 'Deportista Futuro',
                'membership_code': 'DEP-2026124',
                'phone': '987654321',
                'sport': 'natacion',
                'skill_level': 'principiante',
                'birth_date': (date.today() + timedelta(days=1)).isoformat(),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)


class SecurityFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='deportista',
            password='ClaveSegura-2026',
        )
        self.profile = AthleteProfile.objects.create(
            user=self.user,
            full_name='Deportista Prueba',
            membership_code='DEP-2026002',
            email='deportista@example.com',
            phone='987654321',
            sport='basquetbol',
            skill_level='intermedio',
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_registered_profile_can_access_dashboard(self):
        self.client.login(username='deportista', password='ClaveSegura-2026')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'deportista')
        self.assertContains(response, 'Básquetbol')

    def test_permission_view_requires_view_permission(self):
        self.client.login(username='deportista', password='ClaveSegura-2026')
        response = self.client.get(reverse('athlete_list'))
        self.assertEqual(response.status_code, 403)

        permission = Permission.objects.get(codename='view_athleteprofile')
        self.user.user_permissions.add(permission)
        response = self.client.get(reverse('athlete_list'))
        self.assertEqual(response.status_code, 200)

    def test_response_has_security_headers(self):
        response = self.client.get(reverse('home'))
        self.assertIn('X-Request-ID', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('frame-ancestors', response['Content-Security-Policy'])

    def test_logout_requires_post(self):
        self.client.login(username='deportista', password='ClaveSegura-2026')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
