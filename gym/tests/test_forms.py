from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from gym.forms import ClientRegistrationForm, ScheduleForm, ScheduleSearchForm
from gym.models import TrainerProfile, Specialization, Workout

User = get_user_model()


class ClientRegistrationFormTest(TestCase):
    def test_valid_registration_form(self):
        """Test registration form with valid data"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "testpass123",
            "password2": "testpass123",
            "phone_number": "+380501234567"
        }
        form = ClientRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_number_format(self):
        """Test registration form with invalid phone number"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "testpass123",
            "password2": "testpass123",
            "phone_number": "0501234567"  
        }
        form = ClientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_phone_number_wrong_length(self):
        """Test registration form with wrong phone number length"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "testpass123",
            "password2": "testpass123",
            "phone_number": "+38050123456"  
        }
        form = ClientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_mismatch(self):
        """Test registration form with mismatched passwords"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "testpass123",
            "password2": "differentpass",
            "phone_number": "+380501234567"
        }
        form = ClientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_form_saves_user_with_client_role(self):
        """Test that form saves user with client role"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "testpass123",
            "password2": "testpass123",
            "phone_number": "+380501234567"
        }
        form = ClientRegistrationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.role, "client")
        self.assertTrue(hasattr(user, "client_profile"))


class ScheduleFormTest(TestCase):
    def setUp(self):
        
        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="testpass123",
            role="trainer"
        )
        self.admin_user = User.objects.create_user(
            username="admin1",
            password="testpass123",
            role="admin"
        )

        spec = Specialization.objects.create(name="Yoga")
        self.trainer = TrainerProfile.objects.create(
            user=self.trainer_user,
            specialization=spec
        )

        self.workout = Workout.objects.create(
            name="Morning Yoga",
            description="Relaxing yoga session",
            duration_time=60,
            trainer=self.trainer
        )

    def test_valid_schedule_form(self):
        """Test schedule form with valid data"""
        future_time = timezone.now() + timedelta(days=1)
        data = {
            "workout": self.workout.id,
            "start_time": future_time.strftime("%Y-%m-%dT%H:%M"),
            "capacity": 20
        }
        form = ScheduleForm(data=data, user=self.trainer_user)
        self.assertTrue(form.is_valid())

    def test_schedule_form_past_time_invalid(self):
        """Test that schedule form rejects past time"""
        past_time = timezone.now() - timedelta(days=1)
        data = {
            "workout": self.workout.id,
            "start_time": past_time.strftime("%Y-%m-%dT%H:%M"),
            "capacity": 20
        }
        form = ScheduleForm(data=data, user=self.trainer_user)
        self.assertFalse(form.is_valid())
        self.assertIn("start_time", form.errors)

    def test_trainer_can_only_see_own_workouts(self):
        """Test that trainer can only select their own workouts"""
        other_trainer_user = User.objects.create_user(
            username="trainer2",
            password="testpass123",
            role="trainer"
        )
        other_trainer = TrainerProfile.objects.create(
            user=other_trainer_user,
            specialization=self.trainer.specialization
        )
        other_workout = Workout.objects.create(
            name="Other Workout",
            description="Description",
            duration_time=45,
            trainer=other_trainer
        )

        form = ScheduleForm(user=self.trainer_user)
        workout_ids = [w.id for w in form.fields["workout"].queryset]
        self.assertIn(self.workout.id, workout_ids)
        self.assertNotIn(other_workout.id, workout_ids)

    def test_admin_can_see_all_workouts(self):
        """Test that admin can see all workouts"""
        other_trainer_user = User.objects.create_user(
            username="trainer2",
            password="testpass123",
            role="trainer"
        )
        other_trainer = TrainerProfile.objects.create(
            user=other_trainer_user,
            specialization=self.trainer.specialization
        )
        other_workout = Workout.objects.create(
            name="Other Workout",
            description="Description",
            duration_time=45,
            trainer=other_trainer
        )

        form = ScheduleForm(user=self.admin_user)
        workout_ids = [w.id for w in form.fields["workout"].queryset]
        self.assertIn(self.workout.id, workout_ids)
        self.assertIn(other_workout.id, workout_ids)


class ScheduleSearchFormTest(TestCase):
    def test_empty_search_form_valid(self):
        """Test that empty search form is valid"""
        form = ScheduleSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_date_search_form_valid(self):
        """Test search form with date"""
        data = {
            "date": "2025-12-25",
            "workout_name": ""
        }
        form = ScheduleSearchForm(data=data)
        self.assertTrue(form.is_valid())

    def test_workout_name_search_form_valid(self):
        """Test search form with workout name"""
        data = {
            "date": "",
            "workout_name": "Yoga"
        }
        form = ScheduleSearchForm(data=data)
        self.assertTrue(form.is_valid())

    def test_both_fields_search_form_valid(self):
        """Test search form with both fields"""
        data = {
            "date": "2025-12-25",
            "workout_name": "Yoga"
        }
        form = ScheduleSearchForm(data=data)
        self.assertTrue(form.is_valid())