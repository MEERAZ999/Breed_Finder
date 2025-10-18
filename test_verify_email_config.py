#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Set up Django environment
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breedchat.settings')
django.setup()

# Now we can import Django settings
from django.conf import settings

def print_header(text):
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text.center(60)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def check_verify_email_config():
    print_header("VERIFY EMAIL CONFIGURATION CHECK")
    
    # Check if verify_email is in INSTALLED_APPS
    if 'verify_email.apps.VerifyEmailConfig' in settings.INSTALLED_APPS:
        print_success("verify_email is properly installed in INSTALLED_APPS")
    else:
        print_error("verify_email is NOT in INSTALLED_APPS")
        return False
    
    # Check email settings
    email_settings = {
        'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
        'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', None),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
        'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
    }
    
    all_email_settings_valid = True
    for key, value in email_settings.items():
        if value is None:
            print_error(f"{key} is not configured")
            all_email_settings_valid = False
        else:
            if key == 'EMAIL_HOST_PASSWORD' and value:
                masked_password = '*' * (len(value) if len(value) < 8 else 8)
                print_success(f"{key} is configured [value: {masked_password}]")
            else:
                print_success(f"{key} is configured [value: {value}]")
    
    if not all_email_settings_valid:
        print_error("Some email settings are missing")
    
    # Check verify_email specific settings
    verify_email_settings = {
        'VERIFICATION_SUCCESS_TEMPLATE': getattr(settings, 'VERIFICATION_SUCCESS_TEMPLATE', None),
        'VERIFICATION_FAILED_TEMPLATE': getattr(settings, 'VERIFICATION_FAILED_TEMPLATE', None),
        'HTML_MESSAGE_TEMPLATE': getattr(settings, 'HTML_MESSAGE_TEMPLATE', None),
        'TEXT_MESSAGE_TEMPLATE': getattr(settings, 'TEXT_MESSAGE_TEMPLATE', None),
        'SUBJECT': getattr(settings, 'SUBJECT', None),
        'EMAIL_FROM': getattr(settings, 'EMAIL_FROM', None),
        'EMAIL_TOKEN_LIFE': getattr(settings, 'EMAIL_TOKEN_LIFE', None),
        'EMAIL_PAGE_DOMAIN': getattr(settings, 'EMAIL_PAGE_DOMAIN', None),
        'EMAIL_MULTI_USER': getattr(settings, 'EMAIL_MULTI_USER', None),
    }
    
    all_verify_email_settings_valid = True
    for key, value in verify_email_settings.items():
        if value is None:
            print_error(f"{key} is not configured")
            all_verify_email_settings_valid = False
        else:
            print_success(f"{key} is configured [value: {value}]")
    
    if not all_verify_email_settings_valid:
        print_error("Some verify_email settings are missing")
    
    # Check if templates exist
    template_settings = {
        'VERIFICATION_SUCCESS_TEMPLATE': getattr(settings, 'VERIFICATION_SUCCESS_TEMPLATE', None),
        'VERIFICATION_FAILED_TEMPLATE': getattr(settings, 'VERIFICATION_FAILED_TEMPLATE', None),
        'HTML_MESSAGE_TEMPLATE': getattr(settings, 'HTML_MESSAGE_TEMPLATE', None),
        'TEXT_MESSAGE_TEMPLATE': getattr(settings, 'TEXT_MESSAGE_TEMPLATE', None),
    }
    
    from django.template.loader import get_template
    from django.template.exceptions import TemplateDoesNotExist
    
    all_templates_exist = True
    for key, template_path in template_settings.items():
        if template_path:
            try:
                get_template(template_path)
                print_success(f"Template {template_path} exists")
            except TemplateDoesNotExist:
                print_error(f"Template {template_path} does NOT exist")
                all_templates_exist = False
    
    if not all_templates_exist:
        print_error("Some templates are missing")
    
    # Final verdict
    if all_email_settings_valid and all_verify_email_settings_valid and all_templates_exist:
        print_success("\nAll verify_email configurations are correct!")
        return True
    else:
        print_error("\nSome verify_email configurations are missing or incorrect.")
        return False

if __name__ == "__main__":
    check_verify_email_config()