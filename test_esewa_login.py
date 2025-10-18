#!/usr/bin/env python
import os
import sys
import uuid
import hmac
import hashlib
import base64
import requests
import json
from pathlib import Path
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Set up Django environment
sys.path.append(str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breedchat.settings')

# Import Django settings
import django
django.setup()
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

def test_esewa_login():
    print_header("ESEWA LOGIN TEST")
    
    # Check if eSewa credentials are set
    if not settings.ESEWA_SECRET_KEY or not settings.ESEWA_MERCHANT_CODE:
        print_error("eSewa credentials are not properly configured in settings")
        return False
    
    print_success(f"eSewa Secret Key: {settings.ESEWA_SECRET_KEY[:3]}...{settings.ESEWA_SECRET_KEY[-3:]}")
    print_success(f"eSewa Merchant Code: {settings.ESEWA_MERCHANT_CODE}")
    
    # Generate a test transaction UUID
    transaction_uuid = uuid.uuid4()
    print_success(f"Generated Transaction UUID: {transaction_uuid}")
    
    # Set test amount
    amount = 1000
    print_success(f"Test Amount: {amount}")
    
    # Generate signature for form submission
    message = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_MERCHANT_CODE}"
    print_info(f"Signature Message: {message}")
    
    signature = base64.b64encode(
        hmac.new(
            settings.ESEWA_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()
    
    print_success(f"Generated Signature: {signature}")
    
    # Print form data that would be submitted
    print_info("\nForm data that would be submitted to eSewa:")
    form_data = {
        "amount": amount,
        "tax_amount": 0,
        "total_amount": amount,
        "transaction_uuid": str(transaction_uuid),
        "product_code": settings.ESEWA_MERCHANT_CODE,
        "product_service_charge": 0,
        "product_delivery_charge": 0,
        "success_url": "http://127.0.0.1:8001/payment/success/?payment_id=1",
        "failure_url": "http://127.0.0.1:8001/payment/failed/?payment_id=1",
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature
    }
    
    for key, value in form_data.items():
        print(f"  {key}: {value}")
    
    print_info("\neSewa Test Credentials:")
    print_info("eSewa ID: 9806800001 (or 9806800002/3/4/5)")
    print_info("Password: Nepal@123")
    print_info("MPIN: 1122 (for mobile app)")
    
    print_info("\nTo test eSewa integration:")
    print_info("1. Run the Django server: python manage.py runserver 8001")
    print_info("2. Navigate to a pet's payment page")
    print_info("3. Click 'Pay with eSewa'")
    print_info("4. You should be redirected to the eSewa login page")
    print_info("5. Use the test credentials above to log in")
    
    print_warning("\nNote: If you're seeing a 'Login Error' on the eSewa page, it could be due to:")
    print_warning("1. The eSewa test environment being temporarily unavailable")
    print_warning("2. Incorrect signature generation")
    print_warning("3. Mismatch between your merchant code and the eSewa environment")
    
    return True

if __name__ == "__main__":
    test_esewa_login()