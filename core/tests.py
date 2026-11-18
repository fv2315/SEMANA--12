from datetime import date, timedelta

from django.contrib.auth.models import Permission, User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import (
    AthleteProfileForm,
    AthleteRegistrationForm,
    ContactForm,
    sanitize_input,
)
from .models import AthleteProfile


class ValidationTests(TestCase):
    def test_sanitize_input_trims_and_normalizes_whitespace(self):
        self.assertEqual(sanitize_input('  Ana   María \n Pérez '), 'Ana María Pérez')

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

    def test_registration_post_creates_profile_and_starts_session(self):
        response = self.client.post(
            reverse('register'),
            {
                'full_name': 'Camila Rojas',
                'membership_code': 'DEP-2026031',
                'email': 'camila@example.com',
                'phone': '987654321',
                'sport': 'voleibol',
                'skill_level': 'principiante',
                'birth_date': '',
                'username': 'camila_rojas',
                'password1': 'CanchaSegura-2026!',
                'password2': 'CanchaSegura-2026!',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertTrue(
            AthleteProfile.objects.filter(
                membership_code='DEP-2026031',
                sport='voleibol',
            ).exists()
        )


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
        with self.assertLogs('core.security', level='INFO') as logs:
            response = self.client.get(reverse('home'))
        self.assertIn('X-Request-ID', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertIn('frame-ancestors', response['Content-Security-Policy'])
        self.assertTrue(any('method=GET' in entry for entry in logs.output))

    def test_logout_requires_post(self):
        self.client.login(username='deportista', password='ClaveSegura-2026')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    @override_settings(CSRF_COOKIE_SECURE=True, SESSION_COOKIE_SECURE=True)
    def test_csrf_and_session_cookies_are_secure_when_configured(self):
        response = self.client.get(reverse('register'))
        self.assertTrue(response.cookies['csrftoken']['secure'])
        self.assertEqual(response.cookies['csrftoken']['samesite'], 'Lax')
        self.client.login(username='deportista', password='ClaveSegura-2026')
        self.assertTrue(self.client.cookies['sessionid']['secure'])

    def test_logout_post_rejects_missing_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        response = csrf_client.post(reverse('logout'))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_open_athlete_management(self):
        admin = User.objects.create_superuser(
            username='coach_admin',
            email='coach@example.com',
            password='AdminSeguro-2026!',
        )
        self.client.force_login(admin)
        response = self.client.get(
            reverse('admin:core_athleteprofile_changelist')
        )
        self.assertEqual(response.status_code, 200)

    def test_complete_registration_restricted_admin_logout_flow(self):
        response = self.client.post(
            reverse('register'),
            {
                'full_name': 'Camila Rojas',
                'membership_code': 'DEP-2026032',
                'email': 'camila.flow@example.com',
                'phone': '987654321',
                'sport': 'voleibol',
                'skill_level': 'principiante',
                'birth_date': '',
                'username': 'camila_flow',
                'password1': 'CanchaSegura-2026!',
                'password2': 'CanchaSegura-2026!',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(
            self.client.get(reverse('athlete_list')).status_code,
            403,
        )

        self.client.post(reverse('logout'))
        admin = User.objects.create_superuser(
            username='flow_admin',
            email='flow-admin@example.com',
            password='AdminSeguro-2026!',
        )
        self.client.force_login(admin)
        response = self.client.get(
            reverse('admin:core_athleteprofile_changelist')
        )
        self.assertEqual(response.status_code, 200)

        self.client.post(reverse('logout'))
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_model_form_validates_model_field_rules(self):
        form = AthleteProfileForm(
            instance=self.profile,
            data={
                'full_name': self.profile.full_name,
                'membership_code': 'NO-VALIDO',
                'email': self.profile.email,
                'phone': 'telefono-invalido',
                'sport': self.profile.sport,
                'skill_level': self.profile.skill_level,
                'birth_date': '',
            },
        )
        self.assertFalse(form.is_valid())
        self.assertIn('membership_code', form.errors)
        self.assertIn('phone', form.errors)

    def test_user_supplied_markup_is_html_escaped(self):
        self.profile.full_name = '<script>alert(1)</script>'
        self.profile.save()
        self.client.login(username='deportista', password='ClaveSegura-2026')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, '&lt;Script&gt;Alert(1)&lt;/Script&gt;')
        self.assertNotContains(response, '<script>alert(1)</script>')
