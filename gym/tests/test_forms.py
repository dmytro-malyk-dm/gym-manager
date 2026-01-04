from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from accounts.models import TrainerProfile, Specialization
from gym.forms import ScheduleForm, ScheduleSearchForm, WorkoutForm
from gym.models import Workout

User = get_user_model()


class ScheduleFormTest(TestCase):
    """Test custom ScheduleForm logic"""

    def setUp(self):
        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.admin_user = User.objects.create_user(
            username="admin1",
            password="Pass123!",
            role=User.Role.ADMIN
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
        """Test schedule form with valid future time"""
        future_time = timezone.now() + timedelta(days=1)
        data = {
            "workout": self.workout.id,
            "start_time": future_time.strftime("%Y-%m-%dT%H:%M"),
            "capacity": 20,
        }
        form = ScheduleForm(data=data, user=self.trainer_user)
        self.assertTrue(form.is_valid())

    def test_schedule_form_rejects_past_time(self):
        """Test that form rejects past time"""
        past_time = timezone.now() - timedelta(days=1)
        data = {
            "workout": self.workout.id,
            "start_time": past_time.strftime("%Y-%m-%dT%H:%M"),
            "capacity": 20,
        }
        form = ScheduleForm(data=data, user=self.trainer_user)
        self.assertFalse(form.is_valid())
        self.assertIn("start_time", form.errors)

    def test_trainer_sees_only_own_workouts(self):
        """Test that trainer queryset filtered to their workouts only"""
        other_trainer_user = User.objects.create_user(
            username="trainer2",
            password="Pass123!",
            role=User.Role.TRAINER
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
        workout_ids = list(form.fields["workout"].queryset.values_list("id", flat=True))

        self.assertIn(self.workout.id, workout_ids)
        self.assertNotIn(other_workout.id, workout_ids)

    def test_admin_sees_all_workouts(self):
        """Test that admin sees all workouts in queryset"""
        other_trainer_user = User.objects.create_user(
            username="trainer2",
            password="Pass123!",
            role=User.Role.TRAINER
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
        workout_ids = list(form.fields["workout"].queryset.values_list("id", flat=True))

        self.assertIn(self.workout.id, workout_ids)
        self.assertIn(other_workout.id, workout_ids)


class ScheduleSearchFormTest(TestCase):
    """Test ScheduleSearchForm"""

    def test_empty_search_form_is_valid(self):
        """Test that empty form is valid (all fields optional)"""
        form = ScheduleSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_search_by_date_only(self):
        """Test search with only date"""
        data = {"date": "2025-12-25", "workout_name": ""}
        form = ScheduleSearchForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["workout_name"], "")

    def test_search_by_workout_name_only(self):
        """Test search with only workout name"""
        data = {"date": "", "workout_name": "Yoga"}
        form = ScheduleSearchForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data["date"])

    def test_search_with_both_fields(self):
        """Test search with both fields filled"""
        data = {"date": "2025-12-25", "workout_name": "Yoga"}
        form = ScheduleSearchForm(data=data)
        self.assertTrue(form.is_valid())


class WorkoutFormTest(TestCase):
    """Test custom WorkoutForm logic"""

    def setUp(self):
        self.spec = Specialization.objects.create(name="Yoga")

        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.trainer_profile = TrainerProfile.objects.create(
            user=self.trainer_user,
            specialization=self.spec
        )

        self.admin_user = User.objects.create_user(
            username="admin1",
            password="Pass123!",
            role=User.Role.ADMIN
        )

        self.trainer2_user = User.objects.create_user(
            username="trainer2",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.trainer2_profile = TrainerProfile.objects.create(
            user=self.trainer2_user,
            specialization=self.spec
        )

    def test_trainer_can_only_select_themselves(self):
        """Test that trainer can only see their own profile in queryset"""
        form = WorkoutForm(user=self.trainer_user)

        trainer_ids = list(form.fields["trainer"].queryset.values_list("id", flat=True))
        self.assertIn(self.trainer_profile.id, trainer_ids)
        self.assertNotIn(self.trainer2_profile.id, trainer_ids)
        self.assertEqual(len(trainer_ids), 1)

    def test_admin_can_select_any_trainer(self):
        """Test that admin can see all trainers in queryset"""
        form = WorkoutForm(user=self.admin_user)

        trainer_ids = list(form.fields["trainer"].queryset.values_list("id", flat=True))
        self.assertIn(self.trainer_profile.id, trainer_ids)
        self.assertIn(self.trainer2_profile.id, trainer_ids)

    def test_trainer_field_disabled_for_trainers(self):
        """Test that trainer field is disabled for trainers"""
        form = WorkoutForm(user=self.trainer_user)
        self.assertTrue(form.fields["trainer"].disabled)

    def test_trainer_field_not_disabled_for_admins(self):
        """Test that trainer field is not disabled for admins"""
        form = WorkoutForm(user=self.admin_user)
        self.assertFalse(form.fields["trainer"].disabled)

    def test_valid_workout_creation(self):
        """Test creating workout with valid data"""
        data = {
            "name": "Morning Yoga",
            "description": "Relaxing morning session",
            "duration_time": 60,
            "trainer": self.trainer_profile.id
        }
        form = WorkoutForm(data=data, user=self.admin_user)
        self.assertTrue(form.is_valid())
