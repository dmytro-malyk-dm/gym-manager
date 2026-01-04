from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.forms import ClientRegistrationForm, TrainerCreationForm
from accounts.models import ClientProfile, TrainerProfile, Specialization

User = get_user_model()


class ClientRegistrationFormTest(TestCase):
    """Test custom client registration logic"""

    def test_valid_phone_number_format(self):
        """Test that phone number validation accepts valid Ukrainian format"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "phone_number": "+380501234567",
        }
        form = ClientRegistrationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_number_without_prefix(self):
        """Test that phone without +380 prefix is rejected"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "phone_number": "0501234567",
        }
        form = ClientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_invalid_phone_number_wrong_length(self):
        """Test that phone with incorrect length is rejected"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "phone_number": "+38050123456",
        }
        form = ClientRegistrationForm(data=data)
        self.assertFalse(form.is_valid())

    def test_user_created_with_client_role(self):
        """Test that saved user has client role automatically assigned"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "phone_number": "+380501234567",
        }
        form = ClientRegistrationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.role, "client")
        self.assertTrue(hasattr(user, "client_profile"))
        self.assertEqual(user.client_profile.phone_number, "+380501234567")


class TrainerCreationFormTest(TestCase):
    """Test custom trainer creation/update logic"""

    def setUp(self):
        self.specialization = Specialization.objects.create(name="Yoga")

    def test_create_new_trainer_with_password(self):
        """Test creating new trainer assigns trainer role"""
        data = {
            "username": "newtrainer",
            "email": "trainer@example.com",
            "first_name": "New",
            "last_name": "Trainer",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "bio": "Experienced trainer",
            "specialization": self.specialization.id,
        }
        form = TrainerCreationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()

        self.assertEqual(user.role, "trainer")
        self.assertTrue(hasattr(user, "trainer_profile"))
        self.assertEqual(user.trainer_profile.bio, "Experienced trainer")
        self.assertEqual(user.trainer_profile.specialization, self.specialization)

    def test_update_trainer_without_password_preserves_old_password(self):
        """Test updating trainer without password keeps existing password"""

        user = User.objects.create_user(
            username="trainer1",
            password="OldPass123!",
            role="trainer",
            first_name="John",
            last_name="Doe"
        )
        TrainerProfile.objects.create(
            user=user,
            bio="Old bio",
            specialization=self.specialization
        )

        data = {
            "username": "trainer1",
            "email": "trainer@example.com",
            "first_name": "John",
            "last_name": "Updated",
            "password1": "",
            "password2": "",
            "bio": "Updated bio",
            "specialization": self.specialization.id,
        }
        form = TrainerCreationForm(data=data, instance=user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()

        updated_user.refresh_from_db()
        updated_user.trainer_profile.refresh_from_db()

        self.assertTrue(updated_user.check_password("OldPass123!"))
        self.assertEqual(updated_user.last_name, "Updated")
        self.assertEqual(updated_user.trainer_profile.bio, "Updated bio")

    def test_update_trainer_with_password_changes_password(self):
        """Test updating trainer with new password changes it"""
        user = User.objects.create_user(
            username="trainer1",
            password="OldPass123!",
            role="trainer"
        )
        TrainerProfile.objects.create(user=user, specialization=self.specialization)

        data = {
            "username": "trainer1",
            "email": "trainer@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "NewPass123!",
            "password2": "NewPass123!",
            "bio": "Bio",
            "specialization": self.specialization.id,
        }
        form = TrainerCreationForm(data=data, instance=user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()

        self.assertFalse(updated_user.check_password("OldPass123!"))
        self.assertTrue(updated_user.check_password("NewPass123!"))

    def test_username_validation_skipped_on_update(self):
        """Test that username uniqueness check is skipped when updating same user"""
        user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role="trainer"
        )
        TrainerProfile.objects.create(user=user, specialization=self.specialization)

        data = {
            "username": "trainer1",
            "email": "trainer@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password1": "",
            "password2": "",
            "bio": "Updated",
            "specialization": self.specialization.id,
        }
        form = TrainerCreationForm(data=data, instance=user)
        self.assertTrue(form.is_valid())

    def test_password_mismatch_rejected(self):
        """Test that mismatched passwords are rejected"""
        data = {
            "username": "newtrainer",
            "email": "trainer@example.com",
            "first_name": "New",
            "last_name": "Trainer",
            "password1": "Pass123!",
            "password2": "DifferentPass123!",
            "bio": "Bio",
            "specialization": self.specialization.id,
        }
        form = TrainerCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
