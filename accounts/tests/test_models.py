from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.models import TrainerProfile, ClientProfile, Specialization

User = get_user_model()


class UserModelTest(TestCase):
    """Test custom User model"""

    def test_create_user_with_default_client_role(self):
        """Test that user created with default client role"""
        user = User.objects.create_user(
            username="testuser",
            password="Pass123!"
        )
        self.assertEqual(user.role, User.Role.CLIENT)

    def test_create_user_with_trainer_role(self):
        """Test creating user with trainer role"""
        user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.assertEqual(user.role, "trainer")
        self.assertEqual(user.get_role_display(), "Trainer")

    def test_create_user_with_admin_role(self):
        """Test creating user with admin role"""
        user = User.objects.create_user(
            username="admin1",
            password="Pass123!",
            role=User.Role.ADMIN
        )
        self.assertEqual(user.role, "admin")
        self.assertEqual(user.get_role_display(), "Admin")

    def test_user_str_method(self):
        """Test User __str__ returns username"""
        user = User.objects.create_user(
            username="testuser",
            password="Pass123!"
        )
        self.assertEqual(str(user), "testuser")


class SpecializationModelTest(TestCase):
    """Test Specialization model"""

    def test_create_specialization(self):
        """Test creating a specialization"""
        spec = Specialization.objects.create(name="Yoga")
        self.assertEqual(str(spec), "Yoga")

    def test_specialization_name_unique(self):
        """Test that specialization name must be unique"""
        Specialization.objects.create(name="Yoga")

        with self.assertRaises(Exception):
            Specialization.objects.create(name="Yoga")


class TrainerProfileModelTest(TestCase):
    """Test TrainerProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="trainer1",
            first_name="John",
            last_name="Doe",
            password="Pass123!",
            role=User.Role.TRAINER
        )
        self.specialization = Specialization.objects.create(name="Yoga")

    def test_create_trainer_profile(self):
        """Test creating trainer profile with all fields"""
        trainer = TrainerProfile.objects.create(
            user=self.user,
            specialization=self.specialization,
            bio="Experienced yoga instructor with 10 years of practice"
        )

        self.assertEqual(trainer.user, self.user)
        self.assertEqual(trainer.specialization, self.specialization)
        self.assertEqual(trainer.bio, "Experienced yoga instructor with 10 years of practice")
        self.assertEqual(str(trainer), "trainer1")

    def test_trainer_profile_without_specialization(self):
        """Test creating trainer profile without specialization (nullable)"""
        trainer = TrainerProfile.objects.create(
            user=self.user,
            bio="General fitness trainer"
        )

        self.assertIsNone(trainer.specialization)
        self.assertEqual(trainer.bio, "General fitness trainer")

    def test_trainer_profile_one_to_one_relationship(self):
        """Test that user can have only one trainer profile"""
        TrainerProfile.objects.create(
            user=self.user,
            specialization=self.specialization
        )

        with self.assertRaises(Exception):
            TrainerProfile.objects.create(
                user=self.user,
                specialization=self.specialization
            )

    def test_trainer_profile_cascade_delete(self):
        """Test that deleting user deletes trainer profile"""
        trainer = TrainerProfile.objects.create(
            user=self.user,
            specialization=self.specialization
        )
        trainer_id = trainer.id

        self.user.delete()

        self.assertFalse(TrainerProfile.objects.filter(id=trainer_id).exists())

    def test_specialization_set_null_on_delete(self):
        """Test that deleting specialization sets it to NULL in profile"""
        trainer = TrainerProfile.objects.create(
            user=self.user,
            specialization=self.specialization
        )

        self.specialization.delete()
        trainer.refresh_from_db()

        self.assertIsNone(trainer.specialization)


class ClientProfileModelTest(TestCase):
    """Test ClientProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="client1",
            first_name="Jane",
            last_name="Smith",
            password="Pass123!",
            role=User.Role.CLIENT
        )

    def test_create_client_profile(self):
        """Test creating client profile"""
        client = ClientProfile.objects.create(
            user=self.user,
            phone_number="+380501234567"
        )

        self.assertEqual(client.user, self.user)
        self.assertEqual(client.phone_number, "+380501234567")

    def test_client_profile_str_method(self):
        """Test ClientProfile __str__ method"""
        client = ClientProfile.objects.create(
            user=self.user,
            phone_number="+380501234567"
        )

        self.assertIn("Jane Smith", str(client))
        self.assertIn("+380501234567", str(client))

    def test_client_profile_str_with_no_full_name(self):
        """Test __str__ when user has no first/last name"""
        user = User.objects.create_user(
            username="client2",
            password="Pass123!",
            role=User.Role.CLIENT
        )
        client = ClientProfile.objects.create(
            user=user,
            phone_number="+380509876543"
        )

        self.assertIn("+380509876543", str(client))

    def test_client_profile_one_to_one_relationship(self):
        """Test that user can have only one client profile"""
        ClientProfile.objects.create(
            user=self.user,
            phone_number="+380501234567"
        )

        with self.assertRaises(Exception):
            ClientProfile.objects.create(
                user=self.user,
                phone_number="+380509876543"
            )

    def test_client_profile_cascade_delete(self):
        """Test that deleting user deletes client profile"""
        client = ClientProfile.objects.create(
            user=self.user,
            phone_number="+380501234567"
        )
        client_id = client.id

        self.user.delete()

        self.assertFalse(ClientProfile.objects.filter(id=client_id).exists())
