# Email Verification Setup Guide

## Overview

This guide explains how to set up email verification for the Dog Breed Finder application. The application uses Django's email system to send verification emails to users when they register.

## Configuration Steps

### 1. Email Provider Setup

The application is configured to use Gmail as the email provider. To set this up:

1. You need a Gmail account to send emails from
2. Enable 2-Step Verification on your Google account
   - Go to your Google Account > Security > 2-Step Verification
   - Follow the steps to enable 2-Step Verification
3. Generate an App Password
   - Go to your Google Account > Security > App passwords
   - Select "Mail" as the app and "Other (Custom name)" as the device
   - Enter a name like "Dog Breed Finder" and click "Generate"
   - Copy the 16-character password that appears

### 2. Update Environment Variables

Update the `.env` file with your email credentials:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
```

Replace `your_email@gmail.com` with your actual Gmail address and `your_app_password_here` with the App Password you generated.

### 3. Email Templates

The email templates are located in:
- HTML version: `breed_finder/templates/breed_finder/email/mail_body.html`
- Text version: `breed_finder/templates/breed_finder/email/mail_body.txt`

You can customize these templates to match your branding.

### 4. Testing Email Configuration

#### Using the Test Command

A custom management command is available to test your email configuration:

```bash
python manage.py test_email_config --email your_test_email@example.com
```

This command will:
1. Connect to your configured SMTP server
2. Attempt to login with your credentials
3. Send a test email to the specified address
4. Provide detailed error messages and troubleshooting tips if any step fails

#### Testing the Full Verification Flow

To test the complete email verification process:

1. Start the Django server: `python manage.py runserver`
2. Go to the registration page: `http://127.0.0.1:8000/register/`
3. Fill out the registration form with a valid email address
4. Submit the form
5. Check the email inbox for the verification email
6. Click the verification link in the email

### 5. Troubleshooting

#### Common Error: "Username and Password not accepted"

If you see an error like this in your logs:
```
Error in sending email.
Error code: 535
Error: b'5.7.8 Username and Password not accepted. For more information, go to\n5.7.8  `https://support.google.com/mail/?p=BadCredentials`  - gsmtp'
```

This typically occurs when:

1. **Incorrect App Password**: Ensure you've copied the entire 16-character App Password correctly with no spaces
2. **Using Regular Password**: You must use an App Password, not your regular Google account password
3. **2-Step Verification Not Enabled**: App Passwords only work when 2-Step Verification is enabled
4. **App Password Revoked**: If you've recently reset your security settings, you may need to generate a new App Password

#### Other Common Issues

1. Check that your App Password is correct and entered without spaces
2. Ensure 2-Step Verification is enabled on your Google account
3. Check the Django server logs for any error messages
4. Make sure your Gmail account doesn't have any security restrictions that might block the application
5. Check for security alerts in your Gmail account
6. Verify that the email address in `.env` matches the one you used to generate the App Password

### 6. Production Considerations

For production environments:

1. Consider using a transactional email service like SendGrid, Mailgun, or Amazon SES
2. Update the email settings in `.env` and `settings.py` accordingly
3. Set `DEBUG=False` in your `.env` file
4. Update `EMAIL_PAGE_DOMAIN` to your production domain