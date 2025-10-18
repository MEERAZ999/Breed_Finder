from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Checks and fixes email verification settings'

    def handle(self, *args, **options):
        # Check email settings
        email_host = os.getenv('EMAIL_HOST')
        email_port = os.getenv('EMAIL_PORT')
        email_use_tls = os.getenv('EMAIL_USE_TLS')
        email_host_user = os.getenv('EMAIL_HOST_USER')
        email_host_password = os.getenv('EMAIL_HOST_PASSWORD')
        
        self.stdout.write(self.style.SUCCESS(f"Current Email Settings:"))
        self.stdout.write(f"EMAIL_HOST: {email_host}")
        self.stdout.write(f"EMAIL_PORT: {email_port}")
        self.stdout.write(f"EMAIL_USE_TLS: {email_use_tls}")
        self.stdout.write(f"EMAIL_HOST_USER: {email_host_user}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'*' * 8 if email_host_password else 'Not set'}")
        
        # Check verify_email settings
        self.stdout.write(self.style.SUCCESS(f"\nCurrent Verify Email Settings:"))
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"EMAIL_PAGE_DOMAIN: {settings.EMAIL_PAGE_DOMAIN}")
        self.stdout.write(f"EMAIL_MAIL_SUBJECT: {settings.EMAIL_MAIL_SUBJECT}")
        self.stdout.write(f"EMAIL_MAIL_HTML: {settings.EMAIL_MAIL_HTML}")
        self.stdout.write(f"EMAIL_MAIL_PLAIN: {settings.EMAIL_MAIL_PLAIN}")
        self.stdout.write(f"EMAIL_MAIL_TOKEN_LIFE: {settings.EMAIL_MAIL_TOKEN_LIFE}")
        self.stdout.write(f"EMAIL_MAIL_PAGE_TEMPLATE: {settings.EMAIL_MAIL_PAGE_TEMPLATE}")
        self.stdout.write(f"EMAIL_MULTI_USER: {settings.EMAIL_MULTI_USER}")
        
        # Check template paths
        template_dir = os.path.join(settings.BASE_DIR, 'breed_finder', 'templates')
        html_template = os.path.join(template_dir, settings.EMAIL_MAIL_HTML)
        plain_template = os.path.join(template_dir, settings.EMAIL_MAIL_PLAIN)
        success_template = os.path.join(template_dir, settings.EMAIL_MAIL_PAGE_TEMPLATE)
        
        self.stdout.write(self.style.SUCCESS(f"\nTemplate Paths:"))
        self.stdout.write(f"HTML Template: {html_template} (Exists: {os.path.exists(html_template)})")
        self.stdout.write(f"Plain Template: {plain_template} (Exists: {os.path.exists(plain_template)})")
        self.stdout.write(f"Success Template: {success_template} (Exists: {os.path.exists(success_template)})")
        
        # Provide recommendations
        self.stdout.write(self.style.SUCCESS(f"\nRecommendations:"))
        if not email_host_password or email_host_password == 'your-16-digit-app-password':
            self.stdout.write(self.style.WARNING("- Set a valid EMAIL_HOST_PASSWORD in .env file"))
            self.stdout.write("  For Gmail, you need to generate an App Password:")  
            self.stdout.write("  1. Go to your Google Account > Security > 2-Step Verification")
            self.stdout.write("  2. At the bottom, click 'App passwords'")
            self.stdout.write("  3. Select 'Mail' and 'Other (Custom name)'")
            self.stdout.write("  4. Copy the generated 16-character password to your .env file")
        
        if settings.DEFAULT_FROM_EMAIL != email_host_user:
            self.stdout.write(self.style.WARNING(f"- DEFAULT_FROM_EMAIL ({settings.DEFAULT_FROM_EMAIL}) doesn't match EMAIL_HOST_USER ({email_host_user})"))
            self.stdout.write("  Consider updating DEFAULT_FROM_EMAIL in settings.py to match your email address")
        
        # Check for template issues
        if not os.path.exists(html_template):
            self.stdout.write(self.style.WARNING(f"- HTML template not found at {settings.EMAIL_MAIL_HTML}"))
            self.stdout.write("  Check the path in settings.py and ensure the template exists")
        
        if not os.path.exists(plain_template):
            self.stdout.write(self.style.WARNING(f"- Plain text template not found at {settings.EMAIL_MAIL_PLAIN}"))
            self.stdout.write("  Check the path in settings.py and ensure the template exists")
        
        if not os.path.exists(success_template):
            self.stdout.write(self.style.WARNING(f"- Success template not found at {settings.EMAIL_MAIL_PAGE_TEMPLATE}"))
            self.stdout.write("  Check the path in settings.py and ensure the template exists")