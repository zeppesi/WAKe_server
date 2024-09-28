from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import QuerySet
from rest_framework_simplejwt.tokens import SlidingToken

from accounts.models import CommonProfile, User


class CommonProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


admin.site.register(CommonProfile, CommonProfileAdmin)


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    list_display = ['id', 'email', 'name', 'is_staff']
    ordering = ("-id",)
    search_fields = ('email', 'common_profile__name', )

    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_staff', 'is_superuser', 'groups', 'token')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'is_superuser', 'is_staff', 'is_active', 'groups')}
         ),
    )
    readonly_fields = ('token',)

    def token(self, obj: User):
        jwt_token = str(SlidingToken.for_user(obj))
        return jwt_token

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        queryset = queryset.select_related('common_profile')
        return queryset

    def name(self, obj):
        return obj.common_profile.name


admin.site.register(User, UserAdmin)