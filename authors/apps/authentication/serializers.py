from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from rest_framework import serializers
from django.core.validators import RegexValidator
from rest_framework.validators import UniqueValidator
from random import randint
from .models import User

from .validators import (
    GoogleValidate, FacebookValidate,
    TwitterValidate)


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True,
        validators=[RegexValidator(
            regex="^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
            message="Please ensure your password contains at least one letter and one numeral",
            code='invalid_password')],

        error_messages={
            'min_length': 'Password should be at least 8 characters long',
            'max_length': 'Password should not be longer than 128 characters',
            'blank': 'Password cannot be blank',
            'required': 'Password is required'
        }
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'required': 'Email is required',
                    'blank': 'Email field cannot be empty',
                    'invalid': 'Please enter a valid email address'
                },
                'validators': [
                    UniqueValidator(queryset=User.objects.all(),
                                    message='A user with this email already '
                                            'exists')
                ]
            },

            'username': {
                'error_messages': {
                    'required': 'Username is required',
                    'blank': 'Username field cannot be empty'
                },
                'validators': [
                    UniqueValidator(queryset=User.objects.all(),
                                    message='A user with this username '
                                            'already exists')
                ]
            }
        }

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=300, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        if not user.is_verified:
            raise serializers.ValidationError(
                'This email has not been Verified.'
            )


        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.get_token
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class PasswordResetSerializer(serializers.ModelSerializer):
    """
    serializer for the password reset functionaility view
    """
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email',)
        extra_kwargs = {
            'email': {
                'read_only': True
            }
        }


class SetUpdatedPasswordSerializer(serializers.Serializer):
    """
    serializer for handling PUT view for resetting account password
    """
    password = serializers.CharField(
        max_length=120,
        min_length=8,
        validators=[RegexValidator(
            regex="^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
            message="Please ensure your password contains at least one "
                    "letter and one numeral"
        )],
        write_only=True
    )

    # class Meta:
    #     model = User
    #     fields = ('password',)


class GoogleAuthSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization
    of the request data of google social access_tokens
    """
    access_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token']

    def validate_access_token(self, access_token):
        """
        Validate access_token, decode the access_token  and finally retrieve
        user info to grant access to that user.
        It also associates a user with a matching email to that email.
        """

        decoded_user_data = GoogleValidate.validate_google_token(
            access_token)

        if decoded_user_data is None:
            raise serializers.ValidationError(
                'Invalid token please try again'
            )

        if 'sub' not in decoded_user_data:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.'
            )

        user = User.objects.filter(
            email=decoded_user_data.get('email'))


        if not user.exists():
            user_obj = {
                'social_id': decoded_user_data.get('sub'),
                'username': decoded_user_data.get('email'),
                'email': decoded_user_data.get('email'),
                'password': randint(10000000, 20000000),

            }
            new_user = User.objects.create_user(**user_obj)
            new_user.is_verified = True
            new_user.save()

        authenticated_user = User.objects.get(
            email=decoded_user_data.get('email'))
        return authenticated_user.username

class FacebookAuthSerializer(serializers.ModelSerializer):
    """
        Validate access_token, decode the access_token  and finally retrieve
        user info to grant access to that user.
        It also associates a user with a matching email to that email.
    """
    access_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token']

    def validate_access_token(self, access_token):
        """
        Validate auth_token, decode the auth_token,and finally retrieve user
        info to grant access to that user.
        It also associates a user with a matching email to that email.
        """

        facebook_user_data = FacebookValidate.validate_facebook_token(
            access_token)

        if facebook_user_data is None:
            raise serializers.ValidationError(
                'Invalid token please try again'
            )

        if 'id' not in facebook_user_data:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.'
            )

        user = User.objects.filter(email=facebook_user_data.get('email'))
        if not user.exists():
            user_obj = {
                'social_id': facebook_user_data.get('id'),
                'username': facebook_user_data.get('email'),
                'email': facebook_user_data.get('email'),
                'password': randint(10000000, 20000000)
            }
            new_user = User.objects.create_user(**user_obj)
            new_user.is_verified = True
            new_user.save()

        authenticated_user = User.objects.get(
            email=facebook_user_data.get('email'))
        return authenticated_user.username


class TwitterAuthSerializer(serializers.ModelSerializer):
    """
        Validate access_token, decode the access_token  and finally retrieve
        user info to grant access to that user.
        Currently access to twitter email is not available so we are building
        our own from the unique twitter username.
    """
    access_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['access_token']

    def validate_access_token(self, access_token):
        """
            Validate auth_token, decode the auth_token, retrieve user info and
            create the user/get the user and grant them the access token that
            they need to access other pages.
        """
        twitter_user_data = TwitterValidate.validate_twitter_token(
            access_token)
        if twitter_user_data is None:
            raise serializers.ValidationError(
                'Invalid token please try again'
            )

        if 'id_str' not in twitter_user_data:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.'
            )

        user = User.objects.filter(email=twitter_user_data.get('email'))
        if not user.exists():
            user_obj = {
                'social_id': twitter_user_data.get('id_str'),
                'username': twitter_user_data.get('email'),
                'email': twitter_user_data.get('email'),
                'password': randint(10000000, 20000000)
            }
            new_user = User.objects.create_user(**user_obj)
            new_user.is_verified = True
            new_user.save()

        authenticated_user = User.objects.get(
            email=twitter_user_data.get('email'))
        return authenticated_user.username
