#!/bin/bash

# Simple script to test email configuration

# Check if an email address was provided
if [ -z "$1" ]; then
    echo "Error: Please provide an email address as an argument."
    echo "Usage: ./test_email.sh your_email@example.com"
    exit 1
fi

# Get the email address from the command line argument
EMAIL_ADDRESS=$1

# Display a welcome message
echo "========================================"
echo "Dog Breed Finder - Email Configuration Test"
echo "========================================"
echo ""
echo "This script will test your email configuration by sending a test email to: $EMAIL_ADDRESS"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found in the current directory."
    echo "Please make sure you're running this script from the project root directory."
    exit 1
fi

# Display current email configuration from .env file
echo "Current Email Configuration:"
echo "------------------------"
grep -E "^EMAIL_HOST=|^EMAIL_PORT=|^EMAIL_USE_TLS=|^EMAIL_HOST_USER=" .env
echo "EMAIL_HOST_PASSWORD: [HIDDEN]"
echo ""

# Ask for confirmation before proceeding
read -p "Do you want to proceed with testing this configuration? (y/n): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Test cancelled."
    exit 0
fi

echo ""
echo "Running email configuration test..."
echo ""

# Run the Django management command to test email configuration
python manage.py test_email_config --email "$EMAIL_ADDRESS"

echo ""
echo "Test completed."
echo ""
echo "If you need to update your email configuration, edit the .env file and run this script again."
echo "For more information, see EMAIL_SETUP.md"