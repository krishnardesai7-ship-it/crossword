from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import NewUser

INPUTSTYLE = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
USERNAME_REGEX = ['%','$','&','*','#']

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    ROLE_CHOICES = (
        ('user', 'User'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Account Type', initial='user')

    class Meta:
        model = NewUser
        fields = ('email', 'username', 'first_name', 'country','last_name', 'gender', 'phone_number' ,'id_image')

    def clean_role(self):
        role = self.cleaned_data.get('role', 'user')
        # Server-side security: only an authenticated admin can create another admin
        # Even if someone tampers with the form HTML, this will block them
        if role == 'admin' and not getattr(self, '_request_user_is_admin', False):
            raise ValidationError("You do not have permission to create an Admin account.")
        return role

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        if password1 and len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters")
        return password2

    # def clean_first_name(self):
    #     firstname = self.cleaned_data.get('first_name')
    #     if len(firstname)<6:
    #         raise ValidationError("Fist name must be More 6 Charcaters")
    #     return firstname

    # def clean_last_name(self):
    #     lastname = self.cleaned_data.get('last_name')
    #     if len(lastname)<6:
    #         raise ValidationError("Last name must be More 6 Charcaters")
    #     return lastname
    
    def clean_username(self):
        username = (self.cleaned_data.get('username') or "").strip()
        if not username:
            raise ValidationError("Username is required.")

        if NewUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")

        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if NewUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    # def clean_length(self):
    #     firstname = self.cleaned_data.get('firstname')
    #     lastname = self.cleaned_data.get('lastname')
    #     username = self.cleaned_data.get('username')
    #     if len(lastname)<5:
    #         raise ValidationError("Last name must be More 5 Charcaters")
    #     if len(username)<5:
    #         raise ValidationError("User name must be More 5 Charcaters")
    #     return firstname, lastname, username

    def __init__(self, *args, **kwargs):
        # Extract the request_user kwarg (passed from the view) before calling super()
        request_user = kwargs.pop('request_user', None)
        super(UserCreationForm, self).__init__(*args, **kwargs)

        # Store whether the requester is an admin for use in clean_role()
        self._request_user_is_admin = (
            request_user is not None
            and request_user.is_authenticated
            and (request_user.is_superuser or getattr(request_user, 'is_admin', False) or request_user.is_staff)
        )

        # Dynamically add Admin option ONLY if the creator is already an admin
        if self._request_user_is_admin:
            self.fields['role'].choices = (
                ('user', 'User'),
                ('admin', 'Admin'),
            )

        # Apply Tailwind style + cursor text to all fields
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUTSTYLE
            field.widget.attrs['style'] = 'cursor: text;'

        # Placeholder text for each field
        placeholders = {
            'first_name':    'Enter your first name',
            'last_name':     'Enter your last name',
            'username':      'Choose a username include @',
            'email':         'you@example.com',
            'phone_number':  'e.g. 9876543210',
            'country':       'e.g. India',
            'password1':     'min 8 characters and include $',
            'password2':     'Repeat your password',
        }
        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = placeholder

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        
        # Apply permissions based on validated role
        role = self.cleaned_data.get('role', 'user')
        if role == 'admin' and getattr(self, '_request_user_is_admin', False):
            user.is_staff = True
            user.is_admin = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_admin = False
            user.is_superuser = False

        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = NewUser
        fields = ('email', 'password', 'date_of_birth',
                  'is_active', 'is_admin')


class RegisterForm(forms.ModelForm):
    class Meta:
        model = NewUser
        fields = ('email', 'username', 'first_name', 'last_name')
