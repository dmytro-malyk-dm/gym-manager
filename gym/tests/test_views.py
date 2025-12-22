from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from gym.models import (
    TrainerProfile, ClientProfile, Specialization,
    Workout, Schedule, Booking
)
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class HomeViewTest(TestCase):
    def test_home_page_status_code(self):
        """Test home page loads successfully"""
        response = self.client.get(reverse('gym:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gym/index.html')


class TrainerListViewTest(TestCase):
    def setUp(self):
        self.client_http = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='client'
        )
        self.specialization = Specialization.objects.create(name='Yoga')

    def test_trainer_list_requires_login(self):
        """Test that trainer list requires authentication"""
        response = self.client_http.get(reverse('gym:trainer-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_trainer_list_authenticated(self):
        """Test trainer list loads for authenticated users"""
        self.client_http.login(username='testuser', password='testpass123')
        response = self.client_http.get(reverse('gym:trainer-list'))
        self.assertEqual(response.status_code, 200)


class WorkoutListViewTest(TestCase):
    def setUp(self):
        self.client_http = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='client'
        )

    def test_workout_list_requires_login(self):
        """Test that workout list requires authentication"""
        response = self.client_http.get(reverse('gym:workout-list'))
        self.assertEqual(response.status_code, 302)

    def test_workout_list_authenticated(self):
        """Test workout list loads for authenticated users"""
        self.client_http.login(username='testuser', password='testpass123')
        response = self.client_http.get(reverse('gym:workout-list'))
        self.assertEqual(response.status_code, 200)


class ScheduleListViewTest(TestCase):
    def setUp(self):
        self.client_http = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='client'
        )

    def test_schedule_list_requires_login(self):
        """Test that schedule list requires authentication"""
        response = self.client_http.get(reverse('gym:schedule-list'))
        self.assertEqual(response.status_code, 302)

    def test_schedule_list_authenticated(self):
        """Test that authenticated users can access schedule list"""
        self.client_http.login(username='testuser', password='testpass123')
        response = self.client_http.get(reverse('gym:schedule-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gym/schedule_list.html')

    def test_schedule_list_context_has_search_form(self):
        """Test that schedule list has search form in context"""
        self.client_http.login(username='testuser', password='testpass123')
        response = self.client_http.get(reverse('gym:schedule-list'))
        self.assertIn('search_form', response.context)

    def test_schedule_list_shows_only_future_schedules(self):
        """Test that schedule list shows only upcoming schedules"""
        self.client_http.login(username='testuser', password='testpass123')

        # Create trainer and workout
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123',
            role='trainer'
        )
        spec = Specialization.objects.create(name='Cardio')
        trainer = TrainerProfile.objects.create(
            user=trainer_user,
            specialization=spec
        )
        workout = Workout.objects.create(
            name='HIIT',
            description='High intensity',
            duration_time=45,
            trainer=trainer
        )

        # Create past schedule (should not appear)
        Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() - timedelta(days=1),
            capacity=10
        )

        # Create future schedule (should appear)
        future_schedule = Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10
        )

        response = self.client_http.get(reverse('gym:schedule-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(future_schedule, response.context['schedule_list'])
        self.assertEqual(len(response.context['schedule_list']), 1)


class BookingCreateViewTest(TestCase):
    def setUp(self):
        self.client_http = Client()

        # Create client user
        self.client_user = User.objects.create_user(
            username='client1',
            password='testpass123',
            role='client'
        )
        ClientProfile.objects.create(
            user=self.client_user,
            phone_number=380501234567
        )

        # Create trainer and workout
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123',
            role='trainer'
        )
        spec = Specialization.objects.create(name='Yoga')
        trainer = TrainerProfile.objects.create(
            user=trainer_user,
            specialization=spec
        )
        workout = Workout.objects.create(
            name='Morning Yoga',
            description='Relaxing',
            duration_time=60,
            trainer=trainer
        )

        # Create schedule
        self.schedule = Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10
        )

    def test_booking_requires_login(self):
        """Test that booking requires authentication"""
        url = reverse('gym:schedule-book', kwargs={'pk': self.schedule.pk})
        response = self.client_http.post(url)
        self.assertEqual(response.status_code, 302)

    def test_successful_booking(self):
        """Test successful booking creation"""
        self.client_http.login(username='client1', password='testpass123')
        url = reverse('gym:schedule-book', kwargs={'pk': self.schedule.pk})
        response = self.client_http.post(url)

        # Should redirect to schedule detail
        self.assertEqual(response.status_code, 302)

        # Check booking was created
        self.assertTrue(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).exists()
        )

    def test_duplicate_booking_prevented(self):
        """Test that duplicate bookings are prevented"""
        self.client_http.login(username='client1', password='testpass123')

        # Create first booking
        Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )

        # Try to book again
        url = reverse('gym:schedule-book', kwargs={'pk': self.schedule.pk})
        response = self.client_http.post(url)

        # Should redirect with warning
        self.assertEqual(response.status_code, 302)

        # Check only one booking exists
        self.assertEqual(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).count(),
            1
        )

    def test_booking_full_schedule_prevented(self):
        """Test that booking full schedule is prevented"""
        # Fill the schedule
        for i in range(10):
            user = User.objects.create_user(
                username=f'client{i + 2}',
                password='testpass123',
                role='client'
            )
            ClientProfile.objects.create(
                user=user,
                phone_number=380501234560 + i
            )
            Booking.objects.create(
                client=user,
                schedule=self.schedule
            )

        # Try to book
        self.client_http.login(username='client1', password='testpass123')
        url = reverse('gym:schedule-book', kwargs={'pk': self.schedule.pk})
        response = self.client_http.post(url)

        # Should redirect with error
        self.assertEqual(response.status_code, 302)

        # Check booking was not created
        self.assertFalse(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).exists()
        )


class BookingCancelViewTest(TestCase):
    def setUp(self):
        self.client_http = Client()

        # Create client user
        self.client_user = User.objects.create_user(
            username='client1',
            password='testpass123',
            role='client'
        )
        ClientProfile.objects.create(
            user=self.client_user,
            phone_number=380501234567
        )

        # Create trainer and workout
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123',
            role='trainer'
        )
        spec = Specialization.objects.create(name='Yoga')
        trainer = TrainerProfile.objects.create(
            user=trainer_user,
            specialization=spec
        )
        workout = Workout.objects.create(
            name='Morning Yoga',
            description='Relaxing',
            duration_time=60,
            trainer=trainer
        )

        # Create schedule and booking
        self.schedule = Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10
        )
        self.booking = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )

    def test_cancel_booking_success(self):
        """Test successful booking cancellation"""
        self.client_http.login(username='client1', password='testpass123')
        url = reverse('gym:schedule-cancel', kwargs={'pk': self.schedule.pk})
        response = self.client_http.post(url)

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Check booking was deleted
        self.assertFalse(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).exists()
        )


class ClientRegistrationViewTest(TestCase):
    def test_registration_page_loads(self):
        """Test registration page loads"""
        response = self.client.get(reverse('gym:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gym/register.html')

    def test_successful_registration(self):
        """Test successful client registration"""
        data = {
            'username': 'newclient',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'Client',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'phone_number': '+380501234567'
        }
        response = self.client.post(reverse('gym:register'), data)

        # Should redirect to home
        self.assertEqual(response.status_code, 302)

        # Check user was created
        self.assertTrue(User.objects.filter(username='newclient').exists())
        user = User.objects.get(username='newclient')
        self.assertEqual(user.role, 'client')

        # Check client profile was created
        self.assertTrue(ClientProfile.objects.filter(user=user).exists())