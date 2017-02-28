from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def _create(self, email, first_name, last_name, password):
        if not email:
            raise ValueError("Email addresses are required for users.")

        user = self.model(email=UserManager.normalize_email(email),
                          first_name=first_name,
                          last_name=last_name)

        user.set_password(password)

        return user

    def create_user(self, email, first_name, last_name, password=None):
        user = self._create(email, first_name, last_name, password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self._create(email, first_name, last_name, password)
        user.is_staff = True
        user.save()
        return user
