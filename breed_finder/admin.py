from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Pet, UserProfile

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'breed', 'get_age_display', 'gender', 'status')
    list_filter = ('status', 'gender', 'breed')
    search_fields = ('name', 'breed')
    
    def get_age_display(self, obj):
        return obj.age_display
    get_age_display.short_description = 'Age'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_email_verified', 'date_joined', 'is_staff')
    list_filter = ('is_email_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('-date_joined',)
    inlines = (UserProfileInline,)

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('created_at',)
