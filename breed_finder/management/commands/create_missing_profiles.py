from django.core.management.base import BaseCommand
from breed_finder.models import CustomUser, UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile objects for users that do not have one'

    def handle(self, *args, **options):
        users_without_profiles = []
        for user in CustomUser.objects.all():
            try:
                # Try to access the profile
                profile = user.profile
            except UserProfile.DoesNotExist:
                # If profile doesn't exist, add user to the list
                users_without_profiles.append(user)

        self.stdout.write(self.style.SUCCESS(f"Found {len(users_without_profiles)} users without profiles"))

        # Create profiles for users without them
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f"Created profile for {user.email}"))

        self.stdout.write(self.style.SUCCESS("Done creating profiles!"))