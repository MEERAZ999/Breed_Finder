# eSewa Payment Integration Guide

## Overview
This guide provides information on integrating and testing eSewa payment gateway in the BreedChat application.

## Test Credentials

### eSewa Test Account
- **eSewa ID**: 9806800001 (or 9806800002/3/4/5)
- **Password**: Nepal@123
- **MPIN**: 1122 (for mobile app)

### Merchant Credentials
- **Merchant Code**: EPAYTEST
- **Secret Key**: 8gBm/:&EnhH.1/q

## Integration Details

### Form Parameters
The following parameters are required for eSewa payment form submission:

```python
form_data = {
    "amount": amount,                   # Main amount without taxes or charges
    "tax_amount": 0,                   # Tax amount if applicable
    "total_amount": amount,            # Total amount including taxes and charges
    "transaction_uuid": str(uuid.uuid4()),  # Unique transaction identifier
    "product_code": settings.ESEWA_MERCHANT_CODE,  # Your merchant code
    "product_service_charge": 0,      # Service charge if applicable
    "product_delivery_charge": 0,     # Delivery charge if applicable
    "success_url": "http://your-domain.com/success",  # Redirect URL on success
    "failure_url": "http://your-domain.com/failure",  # Redirect URL on failure
    "signed_field_names": "total_amount,transaction_uuid,product_code",  # Fields included in signature
    "signature": signature             # HMAC-SHA256 signature
}
```

### Signature Generation
The signature is generated using HMAC-SHA256 with the following format:

```python
# Message format
message = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={merchant_code}"

# Signature generation
signature = base64.b64encode(
    hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
).decode()
```

## Testing Process

1. Run the Django server: `python manage.py runserver 8001`
2. Navigate to a pet's payment page
3. Click 'Pay with eSewa'
4. You should be redirected to the eSewa login page
5. Use the test credentials above to log in

## Troubleshooting

If you're seeing a 'Login Error' on the eSewa page, it could be due to:

1. The eSewa test environment being temporarily unavailable
2. Incorrect signature generation
3. Mismatch between your merchant code and the eSewa environment

### Debugging Steps

1. Verify that your merchant code and secret key match the test environment credentials
2. Check that the signature is being generated correctly
3. Ensure all required form fields are included and properly formatted
4. Verify that the success and failure URLs are accessible

## Test Script

A test script (`test_esewa_login.py`) is available in the project root to verify your eSewa integration. Run it with:

```bash
python test_esewa_login.py
```

This script will:
- Verify your eSewa credentials are properly configured
- Generate a test transaction UUID
- Create a proper signature
- Display the form data that would be submitted

## Production Migration

When moving to production:

1. Replace the test merchant code and secret key with production credentials
2. Update the success and failure URLs to use your production domain
3. Perform thorough testing with real transactions (small amounts)
4. Implement proper error handling and transaction logging