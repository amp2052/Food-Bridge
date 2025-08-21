from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FoodDonation, FoodRequest, Donation, Campaign, SystemStats, AuditLog, UserProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role Info', {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2', 'first_name', 'last_name', 'is_staff', 'is_active')}
        ),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

# ✅ Register other models
admin.site.register(FoodDonation)
admin.site.register(FoodRequest)
admin.site.register(Donation)
admin.site.register(Campaign)
admin.site.register(SystemStats)
admin.site.register(AuditLog)
admin.site.register(UserProfile)