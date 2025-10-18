# Management Commands

This directory contains custom Django management commands for the Dog Breed Finder application.

## Available Commands

### test_email_config

This command tests your email configuration by attempting to connect to the SMTP server, login with your credentials, and send a test email.

#### Usage

```bash
python manage.py test_email_config --email recipient@example.com
```

Replace `recipient@example.com` with the email address where you want to receive the test email.

#### What it does

1. Connects to the SMTP server specified in your settings
2. Attempts to login with your credentials
3. Sends a test email to the specified recipient
4. Provides detailed error messages and troubleshooting tips if any step fails

#### Example output (success)

```
Testing email configuration...
Using EMAIL_HOST: smtp.gmail.com
Using EMAIL_PORT: 587
Using EMAIL_USE_TLS: True
Using EMAIL_HOST_USER: your_email@gmail.com
EMAIL_HOST_PASSWORD: [HIDDEN]
Attempting to connect to smtp.gmail.com:587...
Successfully connected to SMTP server
Attempting to login with your_email@gmail.com...
Successfully logged in to SMTP server
Creating test email to recipient@example.com...
Sending test email...
Test email sent successfully!
Please check recipient@example.com for the test email
```

#### Example output (failure)

```
Testing email configuration...
Using EMAIL_HOST: smtp.gmail.com
Using EMAIL_PORT: 587
Using EMAIL_USE_TLS: True
Using EMAIL_HOST_USER: your_email@gmail.com
EMAIL_HOST_PASSWORD: [HIDDEN]
Attempting to connect to smtp.gmail.com:587...
Successfully connected to SMTP server
Attempting to login with your_email@gmail.com...
Error: (535, b'5.7.8 Username and Password not accepted. For more information, go to\n5.7.8  https://support.google.com/mail/?p=BadCredentials - gsmtp')
Email configuration test failed

This appears to be an authentication error:
1. Make sure 2-Step Verification is enabled on your Google account
2. Use an App Password, not your regular Google password
3. Ensure the App Password is entered correctly (16 characters, no spaces)
4. Verify that EMAIL_HOST_USER matches the Gmail account used to generate the App Password

For more troubleshooting help, see EMAIL_SETUP.md
```