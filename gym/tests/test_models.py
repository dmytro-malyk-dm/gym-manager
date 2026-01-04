from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from accounts.models import TrainerProfile, ClientProfile, Specialization
from gym.models import Workout, Schedule, Booking

User = get_user_model()


class WorkoutModelTest(TestCase):
    """Test Workout model"""

    def setUp(self):
        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.specialization = Specialization.objects.create(name="Cardio")
        self.trainer = TrainerProfile.objects.create(
            user=self.trainer_user,
            specialization=self.specialization
        )

    def test_create_workout(self):
        """Test creating a workout with all required fields"""
        workout = Workout.objects.create(
            name="HIIT Training",
            description="High intensity interval training for fat burning",
            duration_time=45,
            trainer=self.trainer
        )

        self.assertEqual(workout.name, "HIIT Training")
        self.assertEqual(workout.duration_time, 45)
        self.assertEqual(workout.trainer, self.trainer)
        self.assertEqual(str(workout), "HIIT Training")

    def test_workout_trainer_required(self):
        """Test that workout requires a trainer"""
        with self.assertRaises(Exception):
            Workout.objects.create(
                name="HIIT Training",
                description="Description",
                duration_time=45
            )

    def test_workout_cascade_delete_on_trainer_delete(self):
        """Test that deleting trainer deletes their workouts"""
        workout = Workout.objects.create(
            name="HIIT Training",
            description="Description",
            duration_time=45,
            trainer=self.trainer
        )
        workout_id = workout.id

        self.trainer.delete()

        self.assertFalse(Workout.objects.filter(id=workout_id).exists())

    def test_trainer_can_have_multiple_workouts(self):
        """Test that trainer can have multiple workouts"""
        workout1 = Workout.objects.create(
            name="HIIT Training",
            description="Description",
            duration_time=45,
            trainer=self.trainer
        )
        workout2 = Workout.objects.create(
            name="Strength Training",
            description="Description",
            duration_time=60,
            trainer=self.trainer
        )

        self.assertEqual(self.trainer.workouts.count(), 2)
        self.assertIn(workout1, self.trainer.workouts.all())
        self.assertIn(workout2, self.trainer.workouts.all())


class ScheduleModelTest(TestCase):
    """Test Schedule model"""

    def setUp(self):
        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.specialization = Specialization.objects.create(name="Cardio")
        self.trainer = TrainerProfile.objects.create(
            user=self.trainer_user,
            specialization=self.specialization
        )
        self.workout = Workout.objects.create(
            name="HIIT Training",
            description="High intensity",
            duration_time=45,
            trainer=self.trainer
        )

    def test_create_schedule(self):
        """Test creating a schedule"""
        start_time = timezone.now() + timedelta(days=1)
        schedule = Schedule.objects.create(
            workout=self.workout,
            start_time=start_time,
            capacity=20
        )

        self.assertEqual(schedule.workout, self.workout)
        self.assertEqual(schedule.capacity, 20)
        self.assertIn("HIIT Training", str(schedule))
        self.assertIn(str(start_time.date()), str(schedule))

    def test_schedule_cascade_delete_on_workout_delete(self):
        """Test that deleting workout deletes its schedules"""
        start_time = timezone.now() + timedelta(days=1)
        schedule = Schedule.objects.create(
            workout=self.workout,
            start_time=start_time,
            capacity=20
        )
        schedule_id = schedule.id

        self.workout.delete()

        self.assertFalse(Schedule.objects.filter(id=schedule_id).exists())

    def test_workout_can_have_multiple_schedules(self):
        """Test that workout can have multiple schedules"""
        schedule1 = Schedule.objects.create(
            workout=self.workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=20
        )
        schedule2 = Schedule.objects.create(
            workout=self.workout,
            start_time=timezone.now() + timedelta(days=2),
            capacity=15
        )

        self.assertEqual(self.workout.schedules.count(), 2)
        self.assertIn(schedule1, self.workout.schedules.all())
        self.assertIn(schedule2, self.workout.schedules.all())


class BookingModelTest(TestCase):
    """Test Booking model"""

    def setUp(self):
        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.specialization = Specialization.objects.create(name="Yoga")
        self.trainer = TrainerProfile.objects.create(
            user=self.trainer_user,
            specialization=self.specialization
        )
        self.workout = Workout.objects.create(
            name="Morning Yoga",
            description="Relaxing yoga session",
            duration_time=60,
            trainer=self.trainer
        )

        self.schedule = Schedule.objects.create(
            workout=self.workout,
            start_time=timezone.now() + timedelta(days=1),
            capacity=10
        )

        self.client_user = User.objects.create_user(
            username="client1",
            password="Pass123!",
            role=User.Role.CLIENT
        )
        ClientProfile.objects.create(
            user=self.client_user,
            phone_number="+380501234567"
        )

    def test_create_booking(self):
        """Test creating a booking"""
        booking = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )

        self.assertEqual(booking.client, self.client_user)
        self.assertEqual(booking.schedule, self.schedule)
        self.assertIsNotNone(booking.created_at)
        self.assertIn("client1", str(booking))
        self.assertIn("Morning Yoga", str(booking))

    def test_booking_unique_constraint(self):
        """Test that client cannot book same schedule twice"""
        Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )

        with self.assertRaises(Exception):
            Booking.objects.create(
                client=self.client_user,
                schedule=self.schedule
            )

    def test_multiple_clients_can_book_same_schedule(self):
        """Test that multiple clients can book the same schedule"""
        client2 = User.objects.create_user(
            username="client2",
            password="Pass123!",
            role=User.Role.CLIENT
        )
        ClientProfile.objects.create(
            user=client2,
            phone_number="+380509876543"
        )

        booking1 = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )
        booking2 = Booking.objects.create(
            client=client2,
            schedule=self.schedule
        )

        self.assertEqual(self.schedule.bookings.count(), 2)
        self.assertIn(booking1, self.schedule.bookings.all())
        self.assertIn(booking2, self.schedule.bookings.all())

    def test_booking_cascade_delete_on_client_delete(self):
        """Test that deleting client deletes their bookings"""
        booking = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )
        booking_id = booking.id

        self.client_user.delete()

        self.assertFalse(Booking.objects.filter(id=booking_id).exists())

    def test_booking_cascade_delete_on_schedule_delete(self):
        """Test that deleting schedule deletes its bookings"""
        booking = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )
        booking_id = booking.id

        self.schedule.delete()

        self.assertFalse(Booking.objects.filter(id=booking_id).exists())

    def test_client_can_book_multiple_schedules(self):
        """Test that client can book multiple different schedules"""
        schedule2 = Schedule.objects.create(
            workout=self.workout,
            start_time=timezone.now() + timedelta(days=2),
            capacity=10
        )

        booking1 = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )
        booking2 = Booking.objects.create(
            client=self.client_user,
            schedule=schedule2
        )

        self.assertEqual(self.client_user.bookings.count(), 2)
        self.assertIn(booking1, self.client_user.bookings.all())
        self.assertIn(booking2, self.client_user.bookings.all())

    def test_booking_created_at_auto_set(self):
        """Test that created_at is automatically set"""
        before_creation = timezone.now()
        booking = Booking.objects.create(
            client=self.client_user,
            schedule=self.schedule
        )
        after_creation = timezone.now()

        self.assertGreaterEqual(booking.created_at, before_creation)
        self.assertLessEqual(booking.created_at, after_creation)
