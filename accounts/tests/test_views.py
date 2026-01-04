from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from accounts.models import TrainerProfile, Specialization

User = get_user_model()


class ClientRegistrationViewTest(TestCase):
    """Test client registration view"""

    def test_registration_creates_user_and_profile(self):
        """Test that registration creates both user and client profile"""
        data = {
            "username": "newclient",
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "Client",
            "password1": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "phone_number": "+380501234567",
        }
        response = self.client.post(reverse("accounts:register"), data)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(User.objects.filter(username="newclient").exists())
        user = User.objects.get(username="newclient")
        self.assertEqual(user.role, "client")

        self.assertTrue(hasattr(user, "client_profile"))


class TrainerListViewTest(TestCase):
    """Test trainer list view access control"""

    def setUp(self):
        self.spec = Specialization.objects.create(name="Yoga")
        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role="trainer"
        )
        TrainerProfile.objects.create(
            user=self.trainer_user,
            specialization=self.spec
        )

    def test_trainer_list_requires_authentication(self):
        """Test that unauthenticated users are redirected"""
        response = self.client.get(reverse("accounts:trainer-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_authenticated_user_can_view_trainers(self):
        """Test that logged in users can view trainer list"""
        client_user = User.objects.create_user(
            username="client1",
            password="Pass123!",
            role="client"
        )
        self.client.login(username="client1", password="Pass123!")

        response = self.client.get(reverse("accounts:trainer-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("trainers", response.context)


class TrainerCreateViewTest(TestCase):
    """Test trainer creation view access control"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin1",
            password="Pass123!",
            role="admin"
        )
        self.trainer_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role="trainer"
        )
        self.client_user = User.objects.create_user(
            username="client1",
            password="Pass123!",
            role="client"
        )
        self.spec = Specialization.objects.create(name="Yoga")

    def test_only_admin_can_create_trainer(self):
        """Test that only admins can access trainer creation"""

        self.client.login(username="admin1", password="Pass123!")
        response = self.client.get(reverse("accounts:trainer-create"))
        self.assertEqual(response.status_code, 200)

        self.client.login(username="trainer1", password="Pass123!")
        response = self.client.get(reverse("accounts:trainer-create"))
        self.assertEqual(response.status_code, 302)

        self.client.login(username="client1", password="Pass123!")
        response = self.client.get(reverse("accounts:trainer-create"))
        self.assertEqual(response.status_code, 302)


class TrainerUpdateViewTest(TestCase):
    """Test trainer update view access control"""

    def setUp(self):
        self.spec = Specialization.objects.create(name="Yoga")

        self.admin_user = User.objects.create_user(
            username="admin1",
            password="Pass123!",
            role="admin"
        )

        self.trainer1_user = User.objects.create_user(
            username="trainer1",
            password="Pass123!",
            role="trainer"
        )
        self.trainer1_profile = TrainerProfile.objects.create(
            user=self.trainer1_user,
            specialization=self.spec,
            bio="Trainer 1 bio"
        )

        self.trainer2_user = User.objects.create_user(
            username="trainer2",
            password="Pass123!",
            role="trainer"
        )
        self.trainer2_profile = TrainerProfile.objects.create(
            user=self.trainer2_user,
            specialization=self.spec,
            bio="Trainer 2 bio"
        )

    def test_admin_can_edit_any_trainer(self):
        """Test that admin can edit any trainer profile"""
        self.client.login(username="admin1", password="Pass123!")
        response = self.client.get(
            reverse("accounts:trainer-update", kwargs={"pk": self.trainer1_profile.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_trainer_can_edit_own_profile(self):
        """Test that trainer can edit their own profile"""
        self.client.login(username="trainer1", password="Pass123!")
        response = self.client.get(
            reverse("accounts:trainer-update", kwargs={"pk": self.trainer1_profile.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_trainer_cannot_edit_other_trainer_profile(self):
        """Test that trainer cannot edit another trainer's profile"""
        self.client.login(username="trainer1", password="Pass123!")
        response = self.client.get(
            reverse("accounts:trainer-update", kwargs={"pk": self.trainer2_profile.pk})
        )

        self.assertEqual(response.status_code, 302)
