from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from gym.models import Workout, Schedule, Booking
from accounts.models import TrainerProfile, ClientProfile, Specialization


User = get_user_model()


class Command(BaseCommand):
    help = "Load demo data for testing (users, trainers, workouts, schedules)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Loading demo data..."))

        # Clear existing data (optional - uncomment if needed)
        # Booking.objects.all().delete()
        # Schedule.objects.all().delete()
        # Workout.objects.all().delete()
        # TrainerProfile.objects.all().delete()
        # ClientProfile.objects.all().delete()
        # User.objects.filter(is_superuser=False).delete()
        # Specialization.objects.all().delete()

        # Create Admin
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@gym.com",
                password="admin123",
                first_name="Admin",
                last_name="User",
                role="admin",
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created admin: admin / admin123"))
        else:
            self.stdout.write(self.style.WARNING("Admin already exists"))

        # Create Specializations
        specializations = [
            "Yoga",
            "CrossFit",
            "Boxing",
            "Pilates",
            "HIIT",
            "Strength Training",
        ]
        spec_objects = []
        for spec_name in specializations:
            spec, created = Specialization.objects.get_or_create(name=spec_name)
            spec_objects.append(spec)
            if created:
                self.stdout.write(f"✓ Created specialization: {spec_name}")

        # Create Trainers
        trainers_data = [
            {
                "username": "trainer_john",
                "email": "john.smith@gym.com",
                "password": "trainer123",
                "first_name": "John",
                "last_name": "Smith",
                "specialization": spec_objects[0],  # Yoga
                "bio": "Certified yoga instructor with 10 years of experience. Specialized in Hatha and Vinyasa yoga. Passionate about helping people find their inner peace and flexibility.",
            },
            {
                "username": "trainer_maria",
                "email": "maria.garcia@gym.com",
                "password": "trainer123",
                "first_name": "Maria",
                "last_name": "Garcia",
                "specialization": spec_objects[1],  # CrossFit
                "bio": "Professional CrossFit coach and former athlete. Level 2 CrossFit trainer with expertise in strength training and functional fitness. Let's achieve your goals together!",
            },
            {
                "username": "trainer_mike",
                "email": "mike.tyson@gym.com",
                "password": "trainer123",
                "first_name": "Mike",
                "last_name": "Tyson",
                "specialization": spec_objects[2],  # Boxing
                "bio": "Former professional boxer with 15 years of experience. Expert in boxing technique, footwork, and conditioning. Train like a champion!",
            },
        ]

        trainer_profiles = []
        for trainer_data in trainers_data:
            if not User.objects.filter(username=trainer_data["username"]).exists():
                user = User.objects.create_user(
                    username=trainer_data["username"],
                    email=trainer_data["email"],
                    password=trainer_data["password"],
                    first_name=trainer_data["first_name"],
                    last_name=trainer_data["last_name"],
                    role="trainer",
                )
                trainer_profile = TrainerProfile.objects.create(
                    user=user,
                    specialization=trainer_data["specialization"],
                    bio=trainer_data["bio"],
                )
                trainer_profiles.append(trainer_profile)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created trainer: {trainer_data["username"]} / trainer123'
                    )
                )
            else:
                trainer_profile = TrainerProfile.objects.get(
                    user__username=trainer_data["username"]
                )
                trainer_profiles.append(trainer_profile)
                self.stdout.write(
                    self.style.WARNING(
                        f'Trainer {trainer_data["username"]} already exists'
                    )
                )

        # Create Clients
        clients_data = [
            {
                "username": "client_alex",
                "email": "alex.johnson@email.com",
                "password": "client123",
                "first_name": "Alex",
                "last_name": "Johnson",
                "phone": "+380501234567",
            },
            {
                "username": "client_emma",
                "email": "emma.wilson@email.com",
                "password": "client123",
                "first_name": "Emma",
                "last_name": "Wilson",
                "phone": "+380502345678",
            },
            {
                "username": "client_david",
                "email": "david.brown@email.com",
                "password": "client123",
                "first_name": "David",
                "last_name": "Brown",
                "phone": "+380503456789",
            },
            {
                "username": "client_sophia",
                "email": "sophia.lee@email.com",
                "password": "client123",
                "first_name": "Sophia",
                "last_name": "Lee",
                "phone": "+380504567890",
            },
        ]

        client_users = []
        for client_data in clients_data:
            if not User.objects.filter(username=client_data["username"]).exists():
                user = User.objects.create_user(
                    username=client_data["username"],
                    email=client_data["email"],
                    password=client_data["password"],
                    first_name=client_data["first_name"],
                    last_name=client_data["last_name"],
                    role="client",
                )
                ClientProfile.objects.create(
                    user=user, phone_number=client_data["phone"]
                )
                client_users.append(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Created client: {client_data["username"]} / client123'
                    )
                )
            else:
                user = User.objects.get(username=client_data["username"])
                client_users.append(user)
                self.stdout.write(
                    self.style.WARNING(
                        f'Client {client_data["username"]} already exists'
                    )
                )

        # Create Workouts
        workouts_data = [
            {
                "name": "Morning Yoga",
                "description": "Start your day with a peaceful yoga session. Perfect for beginners and experienced practitioners. Focus on breathing, flexibility, and mindfulness.",
                "duration_time": 60,
                "trainer": trainer_profiles[0],
            },
            {
                "name": "Power Yoga",
                "description": "Dynamic and challenging yoga practice that builds strength and stamina. Suitable for intermediate to advanced students.",
                "duration_time": 75,
                "trainer": trainer_profiles[0],
            },
            {
                "name": "CrossFit Fundamentals",
                "description": "Learn the basics of CrossFit: proper form, Olympic lifts, and essential movements. Great for beginners to build a strong foundation.",
                "duration_time": 90,
                "trainer": trainer_profiles[1],
            },
            {
                "name": "Advanced CrossFit",
                "description": "High-intensity WOD (Workout of the Day) for experienced CrossFitters. Push your limits with challenging exercises and complex movements.",
                "duration_time": 60,
                "trainer": trainer_profiles[1],
            },
            {
                "name": "Boxing Basics",
                "description": "Learn fundamental boxing techniques: stance, jabs, hooks, and footwork. Get in fighting shape while learning self-defense skills.",
                "duration_time": 60,
                "trainer": trainer_profiles[2],
            },
            {
                "name": "Evening Stretch & Relax",
                "description": "Gentle stretching and relaxation session to wind down after a long day. Reduce stress and improve flexibility with guided stretches.",
                "duration_time": 45,
                "trainer": trainer_profiles[0],
            },
        ]

        workouts = []
        for workout_data in workouts_data:
            workout, created = Workout.objects.get_or_create(
                name=workout_data["name"],
                trainer=workout_data["trainer"],
                defaults={
                    "description": workout_data["description"],
                    "duration_time": workout_data["duration_time"],
                },
            )
            workouts.append(workout)
            if created:
                self.stdout.write(f'✓ Created workout: {workout_data["name"]}')

        # Create Schedules (next 14 days)
        now = timezone.now()
        schedules_created = 0

        schedule_templates = [
            {
                "workout": workouts[0],
                "hour": 7,
                "capacity": 15,
                "days": [1, 3, 5],
            },  # Morning Yoga - Mon, Wed, Fri
            {
                "workout": workouts[1],
                "hour": 10,
                "capacity": 12,
                "days": [2, 4],
            },  # Power Yoga - Tue, Thu
            {
                "workout": workouts[2],
                "hour": 18,
                "capacity": 20,
                "days": [1, 3, 5],
            },  # CrossFit Fundamentals
            {
                "workout": workouts[3],
                "hour": 19,
                "capacity": 10,
                "days": [2, 4, 6],
            },  # Advanced CrossFit
            {
                "workout": workouts[4],
                "hour": 17,
                "capacity": 15,
                "days": [1, 3, 5],
            },  # Boxing
            {
                "workout": workouts[5],
                "hour": 20,
                "capacity": 20,
                "days": [1, 2, 3, 4, 5],
            },  # Evening Stretch
        ]

        for day in range(1, 15):  # Next 14 days
            future_date = now + timedelta(days=day)
            weekday = future_date.weekday() + 1  # Monday = 1, Sunday = 7

            for template in schedule_templates:
                if weekday in template["days"]:
                    start_time = future_date.replace(
                        hour=template["hour"], minute=0, second=0, microsecond=0
                    )

                    schedule, created = Schedule.objects.get_or_create(
                        workout=template["workout"],
                        start_time=start_time,
                        defaults={"capacity": template["capacity"]},
                    )

                    if created:
                        schedules_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"✓ Created {schedules_created} schedules")
        )

        # Create some sample bookings
        if schedules_created > 0 and len(client_users) > 0:
            upcoming_schedules = Schedule.objects.filter(start_time__gte=now).order_by(
                "start_time"
            )[:5]

            bookings_created = 0
            for i, schedule in enumerate(upcoming_schedules):
                if i < len(client_users):
                    booking, created = Booking.objects.get_or_create(
                        client=client_users[i], schedule=schedule
                    )
                    if created:
                        bookings_created += 1

            self.stdout.write(
                self.style.SUCCESS(f"✓ Created {bookings_created} sample bookings")
            )

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 60))
        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("\nTest Accounts:")
        self.stdout.write(self.style.WARNING("Admin:"))
        self.stdout.write("  Username: admin | Password: admin123")
        self.stdout.write(self.style.WARNING("\nTrainers:"))
        self.stdout.write("  Username: trainer_john | Password: trainer123")
        self.stdout.write("  Username: trainer_maria | Password: trainer123")
        self.stdout.write("  Username: trainer_mike | Password: trainer123")
        self.stdout.write(self.style.WARNING("\nClients:"))
        self.stdout.write("  Username: client_alex | Password: client123")
        self.stdout.write("  Username: client_emma | Password: client123")
        self.stdout.write("  Username: client_david | Password: client123")
        self.stdout.write("  Username: client_sophia | Password: client123")
        self.stdout.write("=" * 60 + "\n")
