import sys
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        recipient_email = options.get('email')
        if not recipient_email:
            self.stdout.write(self.style.WARNING('Please provide an email address using --email'))
            return

        self.stdout.write(self.style.NOTICE('Testing email configuration...'))
        self.stdout.write(self.style.NOTICE(f'Using EMAIL_HOST: {settings.EMAIL_HOST}'))
        self.stdout.write(self.style.NOTICE(f'Using EMAIL_PORT: {settings.EMAIL_PORT}'))
        self.stdout.write(self.style.NOTICE(f'Using EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}'))
        self.stdout.write(self.style.NOTICE(f'Using EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}'))
        self.stdout.write(self.style.NOTICE('EMAIL_HOST_PASSWORD: [HIDDEN]'))

        # First, try to connect to the SMTP server
        try:
            self.stdout.write(self.style.NOTICE(f'Attempting to connect to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...'))
            if settings.EMAIL_USE_TLS:
                smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            else:
                smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)

            self.stdout.write(self.style.SUCCESS('Successfully connected to SMTP server'))
            
            # Try to login
            self.stdout.write(self.style.NOTICE(f'Attempting to login with {settings.EMAIL_HOST_USER}...'))
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            self.stdout.write(self.style.SUCCESS('Successfully logged in to SMTP server'))
            
            # Create a test email
            self.stdout.write(self.style.NOTICE(f'Creating test email to {recipient_email}...'))
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = recipient_email
            msg['Subject'] = 'Dog Breed Finder - Email Configuration Test'
            body = 'This is a test email to verify your email configuration is working correctly.'
            msg.attach(MIMEText(body, 'plain'))
            
            # Send the email
            self.stdout.write(self.style.NOTICE('Sending test email...'))
            smtp.sendmail(settings.EMAIL_HOST_USER, recipient_email, msg.as_string())
            smtp.quit()
            
            self.stdout.write(self.style.SUCCESS('Test email sent successfully!'))
            self.stdout.write(self.style.SUCCESS(f'Please check {recipient_email} for the test email'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            self.stdout.write(self.style.ERROR('Email configuration test failed'))
            
            # Provide troubleshooting guidance based on the error
            if '535' in str(e) and 'credentials' in str(e).lower():
                self.stdout.write(self.style.WARNING('\nThis appears to be an authentication error:'))
                self.stdout.write(self.style.WARNING('1. Make sure 2-Step Verification is enabled on your Google account'))
                self.stdout.write(self.style.WARNING('2. Use an App Password, not your regular Google password'))
                self.stdout.write(self.style.WARNING('3. Ensure the App Password is entered correctly (16 characters, no spaces)'))
                self.stdout.write(self.style.WARNING('4. Verify that EMAIL_HOST_USER matches the Gmail account used to generate the App Password'))
            elif 'timeout' in str(e).lower():
                self.stdout.write(self.style.WARNING('\nThis appears to be a connection timeout:'))
                self.stdout.write(self.style.WARNING('1. Check your internet connection'))
                self.stdout.write(self.style.WARNING('2. Verify that EMAIL_HOST and EMAIL_PORT are correct'))
                self.stdout.write(self.style.WARNING('3. Make sure your firewall is not blocking the connection'))
            
            self.stdout.write(self.style.NOTICE('\nFor more troubleshooting help, see EMAIL_SETUP.md'))
            return