import jwt
import os

from datetime import datetime, timedelta, date

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models
from .jwt_generator import jwt_encode, jwt_decode
from rest_framework import exceptions
from .utilities import dispatch_email



class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, username, email, password=None, social_id=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email), social_id=social_id)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser powers.

        Superuser powers means that this use is an admin that can do anything
        they want.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a user no longer wishes to use our platform, they may try to delete
    # there account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. To solve this problem, we
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users, this flag will always be
    # falsed.
    is_staff = models.BooleanField(default=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # More fields required for User social login.
    social_id = models.CharField(db_index=True, null=True, max_length=255)

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case, we want that to be the email field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    @property
    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username
    
    @property
    def get_token(self):
        return jwt_encode(self.pk)

    @staticmethod
    def dispatch_reset_token(serializer, request):
        """
        this method processes the reset token and sends it to the user's
         email
        """
        message = "A link for reseting your password will be sent to the \
             email provided"
        subject = "Password Reset link for Author's Haven User Account"

        if serializer.is_valid(raise_exception=True):
            try:
                user = User.objects.get(email=request.data['email'])
                previous_user_requests = ResetPasswordToken.generate_request_instances(user.id)
                if previous_user_requests < 3:
                    token = jwt_encode(user_id=user.pk, days=1)
                    user.persist_reset_token(user, token)
                    request_message = User.generate_reset_link(token)
                    output = dispatch_email(
                        user_email=user.email,
                        subject=subject,
                        message=request_message
                    )
                    return output
                else:
                    return "You have exceeded the request limit for the past 24hours." \
                         "Wait for at least a day before resubmitting the request" 
            except User.DoesNotExist:
                msg = "User with that email does not exist"
                raise exceptions.AuthenticationFailed(msg)
    @staticmethod
    def generate_reset_link(token_variable):
        """
        uses the token to create a link to be sent to user's email
        """
        link = "{}api/users/reset_password/{}/".format(os.getenv('URL'), token_variable)

        req_message = "This email has requested for a password reset \
            click the link {} to reset your password for author's haven".format(link)
        return req_message

    def persist_reset_token(self, user_details, token_variable):
        """
        takes the token and saves it in the database with relation to user
        """
        reset_token = ResetPasswordToken.objects.create(
            user=user_details,
            token=token_variable
        )
        reset_token.save()
    
    @staticmethod
    def persist_new_password(user_details, password):
        """
        takes the password from PUT reset password view and saves it to the database
        """
        new_password = password
        user = user_details[0]
        user.set_password(new_password)
        user.save()
        return "Password reset successful. you may now log into your account with new credentials"

class ResetPasswordToken(models.Model):
    """
    this class creates a Model for the tokens generated during password reset request
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.CharField(max_length=256)
    created_on = models.DateTimeField(auto_now=True,
        verbose_name='when token was generated')
    class Meta:
        ordering = ('created_on',)
    
    @staticmethod
    def generate_request_instances(user_id):
        """
        this method returns number of password reset requests a user has made
        """
        current_day = date.today()
        print(current_day)
        number_of_requests = ResetPasswordToken.objects.filter(
            user=user_id,
            created_on__startswith=current_day
        ).count()
        return number_of_requests
                