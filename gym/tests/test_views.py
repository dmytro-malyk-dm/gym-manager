from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from accounts.models import TrainerProfile, ClientProfile, Specialization
from gym.models import Workout, Schedule, Booking

User = get_user_model()


class HomeViewTest(TestCase):
    """Test home page view"""

    def test_home_page_accessible(self):
        """Test home page loads successfully"""
        response = self.client.get(reverse("gym:index"))
        self.assertEqual(response.status_code, 200)

    def test_home_page_context_data(self):
        """Test home page has correct context"""
        response = self.client.get(reverse("gym:index"))
        self.assertIn("num_trainers", response.context)
        self.assertIn("num_specialization", response.context)
        self.assertIn("num_clients", response.context)


class WorkoutListViewTest(TestCase):
    """Test workout list view"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="Pass123!",
            role=User.Role.CLIENT
        )

    def test_workout_list_requires_authentication(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.get(reverse("gym:workout-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_authenticated_user_can_view_workouts(self):
        """Test that logged in users can view workouts"""
        self.client.login(username="testuser", password="Pass123!")
        response = self.client.get(reverse("gym:workout-list"))
        self.assertEqual(response.status_code, 200)


class WorkoutDetailViewTest(TestCase):
    """Test workout detail view"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="Pass123!",
            role=User.Role.CLIENT
        )
        spec = Specialization.objects.create(name="Yoga")
        trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        trainer = TrainerProfile.objects.create(
            user=trainer_user,
            specialization=spec
        )
        self.workout = Workout.objects.create(
            name="Morning Yoga",
            description="Description",
            duration_time=60,
            trainer=trainer
        )

    def test_workout_detail_requires_authentication(self):
        """Test that workout detail requires login"""
        response = self.client.get(
            reverse("gym:workout-detail", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_view_workout_detail(self):
        """Test that logged in users can view workout details"""
        self.client.login(username="testuser", password="Pass123!")
        response = self.client.get(
            reverse("gym:workout-detail", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["workout"], self.workout)


class WorkoutCreateViewTest(TestCase):
    """Test workout creation access control"""

    def setUp(self):
        self.spec = Specialization.objects.create(name="Yoga")

        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        TrainerProfile.objects.create(
            user=self.trainer_user,
            specialization=self.spec
        )

        self.admin_user = User.objects.create_user(
            username="admin1",
            password="Pass123!",
            role=User.Role.ADMIN
        )

        self.client_user = User.objects.create_user(
            username="client1",
            password="Pass123!",
            role=User.Role.CLIENT
        )

    def test_trainer_can_create_workout(self):
        """Test that trainers can access workout creation"""
        self.client.login(username="trainer1", password="Pass123!")
        response = self.client.get(reverse("gym:workout-create"))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_workout(self):
        """Test that admins can access workout creation"""
        self.client.login(username="admin1", password="Pass123!")
        response = self.client.get(reverse("gym:workout-create"))
        self.assertEqual(response.status_code, 200)

    def test_client_cannot_create_workout(self):
        """Test that clients cannot access workout creation"""
        self.client.login(username="client1", password="Pass123!")
        response = self.client.get(reverse("gym:workout-create"))
        self.assertEqual(response.status_code, 302)


class WorkoutUpdateViewTest(TestCase):
    """Test workout update access control"""

    def setUp(self):
        self.spec = Specialization.objects.create(name="Yoga")

        self.trainer1_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.trainer1_profile = TrainerProfile.objects.create(
            user=self.trainer1_user,
            specialization=self.spec
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

        self.admin_user = User.objects.create_user(
            username="admin1",
            password="Pass123!",
            role=User.Role.ADMIN
        )

        self.workout = Workout.objects.create(
            name="Morning Yoga",
            description="Description",
            duration_time=60,
            trainer=self.trainer1_profile
        )

    def test_trainer_can_edit_own_workout(self):
        """Test that trainer can edit their own workout"""
        self.client.login(username="trainer1", password="Pass123!")
        response = self.client.get(
            reverse("gym:workout-update", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_trainer_cannot_edit_others_workout(self):
        """Test that trainer cannot edit another trainer's workout"""
        self.client.login(username="trainer2", password="Pass123!")
        response = self.client.get(
            reverse("gym:workout-update", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_admin_can_edit_any_workout(self):
        """Test that admin can edit any workout"""
        self.client.login(username="admin1", password="Pass123!")
        response = self.client.get(
            reverse("gym:workout-update", kwargs={"pk": self.workout.pk})
        )
        self.assertEqual(response.status_code, 200)


class ScheduleListViewTest(TestCase):
    """Test schedule list view"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="Pass123!",
            role=User.Role.CLIENT
        )

    def test_schedule_list_requires_authentication(self):
        """Test that schedule list requires login"""
        response = self.client.get(reverse("gym:schedule-list"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_view_schedules(self):
        """Test that authenticated users can view schedule list"""
        self.client.login(username="testuser", password="Pass123!")
        response = self.client.get(reverse("gym:schedule-list"))
        self.assertEqual(response.status_code, 200)

    def test_schedule_list_shows_only_future_schedules(self):
        """Test that only upcoming schedules are shown"""
        self.client.login(username="testuser", password="Pass123!")

        spec = Specialization.objects.create(name="Cardio")
        trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        trainer = TrainerProfile.objects.create(
            user=trainer_user,
            specialization=spec
        )
        workout = Workout.objects.create(
            name="HIIT",
            description="High intensity",
            duration_time=45,
            trainer=trainer
        )

        Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() - timedelta(days=1),
            capacity=10
        )

        future_schedule = Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10
        )

        response = self.client.get(reverse("gym:schedule-list"))
        self.assertEqual(len(response.context["schedule_list"]), 1)
        self.assertIn(future_schedule, response.context["schedule_list"])


class BookingCreateViewTest(TestCase):
    """Test booking creation view"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client1",
            password="Pass123!",
            role=User.Role.CLIENT
        )
        ClientProfile.objects.create(
            user=self.client_user,
            phone_number="+380501234567"
        )

        spec = Specialization.objects.create(name="Yoga")
        trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        trainer = TrainerProfile.objects.create(
            user=trainer_user,
            specialization=spec
        )
        workout = Workout.objects.create(
            name="Morning Yoga",
            description="Relaxing",
            duration_time=60,
            trainer=trainer
        )

        self.schedule = Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10
        )

    def test_booking_requires_authentication(self):
        """Test that creating booking requires login"""
        url = reverse("gym:schedule-book", kwargs={"pk": self.schedule.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_successful_booking_creation(self):
        """Test successful booking"""
        self.client.login(username="client1", password="Pass123!")
        url = reverse("gym:schedule-book", kwargs={"pk": self.schedule.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).exists()
        )

    def test_duplicate_booking_prevented(self):
        """Test that duplicate bookings are prevented"""
        self.client.login(username="client1", password="Pass123!")

        Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )

        url = reverse("gym:schedule-book", kwargs={"pk": self.schedule.pk})
        self.client.post(url)

        self.assertEqual(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).count(),
            1
        )

    def test_booking_full_schedule_prevented(self):
        """Test that booking full schedule is prevented"""

        for i in range(10):
            user = User.objects.create_user(
                username=f"client{i + 2}",
                password="Pass123!",
                role=User.Role.CLIENT
            )
            ClientProfile.objects.create(
                user=user,
                phone_number=f"+38050123456{i}"
            )
            Booking.objects.create(client=user, schedule=self.schedule)

        self.client.login(username="client1", password="Pass123!")
        url = reverse("gym:schedule-book", kwargs={"pk": self.schedule.pk})
        self.client.post(url)

        self.assertFalse(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).exists()
        )


class BookingCancelViewTest(TestCase):
    """Test booking cancellation view"""

    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client1",
            password="Pass123!",
            role=User.Role.CLIENT
        )
        ClientProfile.objects.create(
            user=self.client_user,
            phone_number="+380501234567"
        )

        spec = Specialization.objects.create(name="Yoga")
        trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        trainer = TrainerProfile.objects.create(
            user=trainer_user,
            specialization=spec
        )
        workout = Workout.objects.create(
            name="Morning Yoga",
            description="Relaxing",
            duration_time=60,
            trainer=trainer
        )

        self.schedule = Schedule.objects.create(
            workout=workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10
        )
        self.booking = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )

    def test_successful_booking_cancellation(self):
        """Test successful cancellation"""
        self.client.login(username="client1", password="Pass123!")
        url = reverse("gym:schedule-cancel", kwargs={"pk": self.schedule.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Booking.objects.filter(
                client=self.client_user,
                schedule=self.schedule
            ).exists()
        )
