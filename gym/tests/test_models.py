from django.test import TestCase

from django.contrib.auth import get_user_model
from gym.models import (
    TrainerProfile,
    ClientProfile,
    Specialization,
    Workout,
    Schedule,
    Booking,
)
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_client_user(self):
        """Test creating a client user"""
        user = User.objects.create_user(
            username="client1", password="testpass123", role="client"
        )
        self.assertEqual(user.role, "client")
        self.assertEqual(str(user), "client1")

    def test_create_trainer_user(self):
        """Test creating a trainer user"""
        user = User.objects.create_user(
            username="trainer1", password="testpass123", role="trainer"
        )
        self.assertEqual(user.role, "trainer")


class TrainerProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="trainer1",
            first_name="John",
            last_name="Doe",
            password="testpass123",
            role="trainer",
        )
        self.specialization = Specialization.objects.create(name="Yoga")

    def test_create_trainer_profile(self):
        """Test creating a trainer profile"""
        trainer = TrainerProfile.objects.create(
            user=self.user,
            specialization=self.specialization,
            bio="Experienced yoga instructor",
        )
        self.assertEqual(str(trainer), "trainer1")
        self.assertEqual(trainer.specialization.name, "Yoga")


class ClientProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="client1", password="testpass123", role="client"
        )

    def test_create_client_profile(self):
        """Test creating a client profile"""
        client = ClientProfile.objects.create(user=self.user, phone_number=380501234567)
        self.assertIn("380501234567", str(client))


class WorkoutModelTest(TestCase):
    def setUp(self):
        self.trainer_user = User.objects.create_user(
            username="trainer1", password="testpass123", role="trainer"
        )
        self.specialization = Specialization.objects.create(name="Cardio")
        self.trainer = TrainerProfile.objects.create(
            user=self.trainer_user, specialization=self.specialization
        )

    def test_create_workout(self):
        """Test creating a workout"""
        workout = Workout.objects.create(
            name="HIIT Training",
            description="High intensity interval training",
            duration_time=45,
            trainer=self.trainer,
        )
        self.assertEqual(str(workout), "HIIT Training")
        self.assertEqual(workout.duration_time, 45)


class ScheduleModelTest(TestCase):
    def setUp(self):
        self.trainer_user = User.objects.create_user(
            username="trainer1", password="testpass123", role="trainer"
        )
        self.specialization = Specialization.objects.create(name="Cardio")
        self.trainer = TrainerProfile.objects.create(
            user=self.trainer_user, specialization=self.specialization
        )
        self.workout = Workout.objects.create(
            name="HIIT Training",
            description="High intensity",
            duration_time=45,
            trainer=self.trainer,
        )

    def test_create_schedule(self):
        """Test creating a schedule"""
        start_time = timezone.now() + timedelta(days=1)
        schedule = Schedule.objects.create(
            workout=self.workout, start_time=start_time, capacity=20
        )
        self.assertIn("HIIT Training", str(schedule))
        self.assertEqual(schedule.capacity, 20)


class BookingModelTest(TestCase):
    def setUp(self):
        self.trainer_user = User.objects.create_user(
            username="trainer1", password="testpass123", role="trainer"
        )
        self.specialization = Specialization.objects.create(name="Yoga")
        self.trainer = TrainerProfile.objects.create(
            user=self.trainer_user, specialization=self.specialization
        )

        self.workout = Workout.objects.create(
            name="Morning Yoga",
            description="Relaxing yoga session",
            duration_time=60,
            trainer=self.trainer,
        )
        self.schedule = Schedule.objects.create(
            workout=self.workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10,
        )

        self.client_user = User.objects.create_user(
            username="client1", password="testpass123", role="client"
        )
        ClientProfile.objects.create(user=self.client_user, phone_number=380501234567)

    def test_create_booking(self):
        """Test creating a booking"""
        booking = Booking.objects.create(
            client=self.client_user, schedule=self.schedule
        )
        self.assertIn("client1", str(booking))
        self.assertEqual(booking.schedule, self.schedule)

    def test_unique_booking_constraint(self):
        """Test that a client cannot book the same schedule twice"""
        Booking.objects.create(client=self.client_user, schedule=self.schedule)
        with self.assertRaises(Exception):
            Booking.objects.create(client=self.client_user, schedule=self.schedule)
