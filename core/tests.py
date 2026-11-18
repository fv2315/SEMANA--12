from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from .forms import ContactForm, StudentRegistrationForm
from .models import StudentProfile


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

    def test_registration_sanitizes_full_name(self):
        form = StudentRegistrationForm(
            data={
                'username': 'ana2026',
                'email': 'ANA@Example.COM',
                'password1': 'ClaveSegura-2026',
                'password2': 'ClaveSegura-2026',
                'full_name': '  Ana   Pérez  ',
                'code': '2026001',
                'phone': '987654321',
                'career': 'sistemas',
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['full_name'], 'Ana Pérez')
        self.assertEqual(form.cleaned_data['email'], 'ana@example.com')


class SecurityFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alumno',
            password='ClaveSegura-2026',
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            full_name='Alumno Prueba',
            code='2026002',
            email='alumno@example.com',
            phone='987654321',
            career='sistemas',
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_registered_profile_can_access_dashboard(self):
        self.client.login(username='alumno', password='ClaveSegura-2026')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'alumno')

    def test_permission_view_requires_view_permission(self):
        self.client.login(username='alumno', password='ClaveSegura-2026')
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 403)

        permission = Permission.objects.get(codename='view_studentprofile')
        self.user.user_permissions.add(permission)
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)

    def test_response_has_security_headers(self):
        response = self.client.get(reverse('home'))
        self.assertIn('X-Request-ID', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('frame-ancestors', response['Content-Security-Policy'])
