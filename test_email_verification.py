#!/usr/bin/env python

import os
import sys
import django
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breedchat.settings')
django.setup()

def test_email_connection():
    # Get email settings from environment variables
    email_host = os.getenv('EMAIL_HOST')
    email_port = int(os.getenv('EMAIL_PORT'))
    email_use_tls = os.getenv('EMAIL_USE_TLS') == 'True'
    email_host_user = os.getenv('EMAIL_HOST_USER')
    email_host_password = os.getenv('EMAIL_HOST_PASSWORD')
    
    print(f"Email Configuration Test")
    print(f"======================")
    print(f"EMAIL_HOST: {email_host}")
    print(f"EMAIL_PORT: {email_port}")
    print(f"EMAIL_USE_TLS: {email_use_tls}")
    print(f"EMAIL_HOST_USER: {email_host_user}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * 8}")
    
    try:
        # Try to connect to the SMTP server
        print(f"\nAttempting to connect to {email_host}:{email_port}...")
        if email_use_tls:
            smtp = smtplib.SMTP(email_host, email_port)
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
        else:
            smtp = smtplib.SMTP(email_host, email_port)

        print("Successfully connected to SMTP server")
        
        # Try to login
        print(f"Attempting to login with {email_host_user}...")
        smtp.login(email_host_user, email_host_password)
        print("Successfully logged in to SMTP server")
        
        # Close the connection
        smtp.quit()
        print("\n✅ Email configuration test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Email configuration test failed")
        
        # Provide troubleshooting guidance based on the error
        if '535' in str(e) and 'credentials' in str(e).lower():
            print("\nThis appears to be an authentication error:")
            print("1. Make sure 2-Step Verification is enabled on your Google account")
            print("2. Use an App Password, not your regular Google password")
            print("3. Ensure the App Password is entered correctly (16 characters, no spaces)")
            print("4. Verify that EMAIL_HOST_USER matches the Gmail account used to generate the App Password")
            print("\nFollow these steps to generate an App Password:")
            print("1. Go to your Google Account settings: https://myaccount.google.com/")
            print("2. Select Security")
            print("3. Under 'Signing in to Google,' select 2-Step Verification")
            print("4. At the bottom of the page, select App passwords")
            print("5. Enter a name that helps you remember where you'll use the app password")
            print("6. Select Generate")
            print("7. Copy the 16-character code shown on your screen")
            print("8. Update the EMAIL_HOST_PASSWORD in your .env file")
        elif 'timeout' in str(e).lower():
            print("\nThis appears to be a connection timeout:")
            print("1. Check your internet connection")
            print("2. Verify that EMAIL_HOST and EMAIL_PORT are correct")
            print("3. Make sure your firewall is not blocking the connection")
        
        return False

def test_verify_email_package():
    print("\nVerify Email Package Test")
    print("========================")
    
    try:
        from verify_email.email_handler import send_verification_email
        print("✅ verify_email package is installed")
        
        # Check if the package is properly configured in settings.py
        if 'verify_email' in settings.INSTALLED_APPS:
            print("✅ verify_email is in INSTALLED_APPS")
        else:
            print("❌ verify_email is not in INSTALLED_APPS")
        
        # Check for required settings
        required_settings = [
            'VERIFICATION_SUCCESS_TEMPLATE', 
            'VERIFICATION_FAILED_TEMPLATE',
            'HTML_MESSAGE_TEMPLATE',
            'SUBJECT',
            'EMAIL_PAGE_DOMAIN',
            'EMAIL_FROM',
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                print(f"✅ {setting} is configured")
            else:
                print(f"❌ {setting} is not configured")
        
        return True
    except ImportError:
        print("❌ verify_email package is not installed")
        print("Run: pip install django-verify-email")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Running Email Verification Tests\n")
    
    # Test email connection
    connection_success = test_email_connection()
    
    # Test verify_email package
    package_success = test_verify_email_package()
    
    # Summary
    print("\nTest Summary")
    print("===========")
    print(f"Email Connection: {'✅ Success' if connection_success else '❌ Failed'}")
    print(f"Verify Email Package: {'✅ Success' if package_success else '❌ Failed'}")
    
    if not connection_success:
        print("\n⚠️ Email verification will not work until the email connection is fixed.")
        print("Please update your .env file with the correct App Password.")
    
    if connection_success and package_success:
        print("\n🎉 All tests passed! Email verification should be working correctly.")