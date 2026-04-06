from django.db import models


from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin, Permission
)
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a user with email/username and optional profile fields.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('Must have username')

        if not password or len(password) < 8:
            raise ValueError('Password Must be over 8 Char')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=extra_fields.get("first_name", ""),
            last_name=extra_fields.get("last_name", ""),
            gender=extra_fields.get("gender", ""),
            country=extra_fields.get("country"),
            phone_number=extra_fields.get("phone_number"),
            date_of_birth=extra_fields.get("date_of_birth"),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a superuser.
        """
        user = self.create_user(
            email,
            username,
            password=password,
            **extra_fields,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


USERNAME_REGEX = '^[a-zA-Z0-9.@+-]*$'



class NewUser(PermissionsMixin, AbstractBaseUser):
    class GENDER(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        max_length=125,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message='Username must be alpahnmeric or contain any of the following: ". @ + -"',
                code='invalid_username'
            ),
        ],
        unique=True
    )
    first_name = models.CharField(max_length=125)
    last_name = models.CharField(max_length=125)
    id_image = models.ImageField(upload_to="id-images/", null=True, blank=True)
    country = models.CharField(max_length=125, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER.choices)
    phone_number = models.IntegerField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

#####################################################################################
#####################################################################################
#####################################################################################

# from models.py
# add PermissionsMixin
# remove has_perm and has_module_perms

# from admin.py
# fieldsets -> Permissions -> add ('groups', 'user_permissions')
# remove filter_horizontal


# class Profile(models.Model):
#     class STATE_CHOICES(models.TextChoices):
#         MALE = "MA", 'Male'
#         FEMALE = "FA", "Female"

#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     username = models.CharField(max_length=50, unique=True)
#     email = models.EmailField()
#     id_image = models.ImageField(upload_to="id-images/")
#     phone_number = models.IntegerField()
#     status = models.CharField(max_length=6, choices=STATE_CHOICES.choices)

    
