#!/usr/bin/env python

import requests
import base64
import hmac
import hashlib
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get eSewa credentials from environment variables
ESEWA_SECRET_KEY = os.getenv('ESEWA_SECRET_KEY')
ESEWA_MERCHANT_CODE = os.getenv('ESEWA_MERCHANT_CODE')

def test_esewa_signature():
    # Create a test transaction UUID
    transaction_uuid = str(uuid.uuid4())
    total_amount = "1000"
    
    # Generate signature
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={ESEWA_MERCHANT_CODE}"
    signature = base64.b64encode(
        hmac.new(
            ESEWA_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()
    
    print(f"Test eSewa Signature Generation")
    print(f"============================")
    print(f"Transaction UUID: {transaction_uuid}")
    print(f"Total Amount: {total_amount}")
    print(f"Product Code: {ESEWA_MERCHANT_CODE}")
    print(f"Message: {message}")
    print(f"Generated Signature: {signature}")
    print("\nThis signature would be used in the eSewa payment form.")
    print("\nTo test the eSewa integration:")
    print("1. Create a payment record in the database")
    print("2. Generate a signature using the transaction UUID")
    print("3. Submit the form to eSewa with the signature")
    print("4. eSewa will redirect back to your success/failure URL")
    
    # Verify the signature format
    if len(signature) > 0:
        print("\n✅ Signature generation successful!")
    else:
        print("\n❌ Signature generation failed!")

if __name__ == "__main__":
    if not ESEWA_SECRET_KEY or not ESEWA_MERCHANT_CODE:
        print("Error: eSewa credentials not found in environment variables.")
        print("Make sure ESEWA_SECRET_KEY and ESEWA_MERCHANT_CODE are set in your .env file.")
    else:
        test_esewa_signature()