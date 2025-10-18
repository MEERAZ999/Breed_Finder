import json
import uuid
import hmac
import hashlib
import base64
import requests
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from .models import Payment
from breed_finder.models import Pet

@login_required
def payment_page(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if pet.status != 'AVAILABLE':
        messages.error(request, 'This pet is not available for adoption.')
        return redirect('breed_finder:pet_detail', pet_id=pet_id)

    # Create a pending payment record with a unique transaction ID
    # Format the UUID as a string without dashes to avoid eSewa validation issues
    unique_id = str(uuid.uuid4()).replace('-', '')[:20]
    payment = Payment.objects.create(
        user=request.user,
        pet=pet,
        amount=pet.price,  # Use the pet's price from the model
        payment_method='PENDING',
        payment_status='PENDING',
        transaction_uuid=unique_id
    )

    # Build eSewa success and failure URLs with the transaction UUID
    esewa_success_url = request.build_absolute_uri(reverse('payment:esewa_verify') + f'?oid={unique_id}')
    esewa_failure_url = request.build_absolute_uri(reverse('payment:payment_failed') + f'?oid={unique_id}')

    context = {
        'pet': pet,
        'payment': payment,
        'khalti_public_key': settings.KHALTI_PUBLIC_KEY,
        'esewa_merchant_code': settings.ESEWA_MERCHANT_CODE,
        'esewa_product_code': settings.ESEWA_MERCHANT_CODE,  # Using merchant code as product code
        'esewa_success_url': esewa_success_url,
        'esewa_failure_url': esewa_failure_url,
        'success_url': request.build_absolute_uri(reverse('payment:payment_success')),
        'failure_url': request.build_absolute_uri(reverse('payment:payment_failed'))
    }
    return render(request, 'payment/payment.html', context)

@csrf_exempt
def khalti_verify(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_id = data.get('payment_id')
            payment = get_object_or_404(Payment, id=payment_id)

            # Initiate Khalti payment
            url = "https://a.khalti.com/api/v2/epayment/initiate/"
            payload = {
                "return_url": request.build_absolute_uri(reverse('payment:payment_success')),
                "website_url": request.build_absolute_uri('/'),
                "amount": int(payment.amount * 100),  # Convert to paisa
                "purchase_order_id": str(payment.transaction_uuid),
                "purchase_order_name": f"Pet Adoption - {payment.pet.name}",
                "customer_info": {
                    "name": request.user.get_full_name() or request.user.username,
                    "email": request.user.email,
                    "phone": "9800000000"  # Should be from user profile
                }
            }
            
            headers = {
                "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                payment.payment_method = 'KHALTI'
                payment.payment_status = 'INITIATED'
                payment.pidx = response_data.get('pidx')
                payment.payment_url = response_data.get('payment_url')
                payment.save()

                return JsonResponse({
                    'success': True,
                    'payment_url': response_data.get('payment_url')
                })

            return JsonResponse({
                'success': False,
                'message': 'Payment initiation failed',
                'details': response.json() if response.status_code != 500 else 'Internal Server Error'
            })

        except Exception as e:
            # Handle general exceptions
            error_msg = f'Error during payment verification: {str(e)}'
            payment.mark_as_failed(error_msg)
            messages.error(request, 'An unexpected error occurred during payment verification.')
            return redirect('payment:payment_failed')
    
    return redirect('payment:payment_failed')

@csrf_exempt
@require_POST
def get_esewa_signature(request):
    try:
        # Parse the request body
        data = json.loads(request.body)
        message = data.get('message')
        api_version = data.get('api_version', 'v2')  # Default to v2 API
        payment_id = data.get('payment_id')
        
        if not message:
            return JsonResponse({'success': False, 'error': 'Message is required'})
        
        # If payment_id is provided, update the transaction_uuid to ensure uniqueness
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
                # Generate a new transaction UUID if this is a retry or the payment failed
                if payment.payment_status == 'FAILED' or payment.payment_status == 'PENDING':
                    # Generate a new UUID without dashes and limit to 20 chars
                    new_uuid = str(uuid.uuid4()).replace('-', '')[:20]
                    payment.transaction_uuid = new_uuid
                    payment.save()
                    print(f"Generated new transaction UUID for payment {payment_id}: {new_uuid}")
                    
                    # Update the message with the new transaction UUID
                    # Extract the parts of the message
                    parts = message.split(',')
                    updated_parts = []
                    for part in parts:
                        if part.startswith('transaction_uuid='):
                            updated_parts.append(f'transaction_uuid={new_uuid}')
                        else:
                            updated_parts.append(part)
                    
                    message = ','.join(updated_parts)
            except Payment.DoesNotExist:
                pass  # Continue with the original message if payment not found
        
        # Generate HMAC-SHA256 signature for eSewa v2 API
        signature = base64.b64encode(
            hmac.new(
                settings.ESEWA_SECRET_KEY.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        ).decode()
        
        return JsonResponse({
            'success': True,
            'signature': signature,
            'message': message  # Return the possibly updated message
        })
    except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def esewa_verify(request):
    if request.method == 'GET':
        try:
            # Get the oid from the request (transaction_uuid)
            oid = request.GET.get('oid')  # This is our transaction_uuid
            data = request.GET.get('data')  # Base64 encoded data from eSewa v2 API
            
            # Log the received parameters for debugging
            print(f"eSewa v2 callback received: oid={oid}, data={data}")
            
            # Find the payment by transaction_uuid
            try:
                payment = Payment.objects.get(transaction_uuid=oid)
            except Payment.DoesNotExist:
                # If payment not found by transaction_uuid, log this for debugging
                print(f"Payment with transaction_uuid={oid} not found")
                # Try to find any pending payment for the current user if logged in
                if request.user.is_authenticated:
                    try:
                        # Look for the most recent pending payment for this user
                        payment = Payment.objects.filter(
                            user=request.user, 
                            payment_status='PENDING'
                        ).order_by('-created_at').first()
                        
                        if payment:
                            # Update the transaction UUID to match the one from eSewa
                            payment.transaction_uuid = oid
                            payment.save()
                            print(f"Found pending payment {payment.id} for user {request.user.username}, updated transaction_uuid to {oid}")
                        else:
                            # No pending payment found
                            print(f"No pending payment found for user {request.user.username}")
                            return redirect(f"{reverse('payment:payment_failed')}?oid={oid}&error=no_pending_payment")
                    except Exception as e:
                        print(f"Error finding pending payment: {str(e)}")
                        return redirect(f"{reverse('payment:payment_failed')}?oid={oid}&error=find_payment_error")
                else:
                    # User not logged in, can't find their payment
                    return redirect(f"{reverse('payment:payment_failed')}?oid={oid}&error=not_logged_in")
            
            # Check if payment is already completed to avoid duplicate processing
            if payment.payment_status == 'COMPLETED':
                messages.info(request, 'This payment has already been processed.')
                return redirect(f"{reverse('payment:payment_success')}?payment_id={payment.id}")
            
            # Check if we're in development mode
            if settings.DEBUG:
                # In development mode, we'll simulate a successful payment
                payment.payment_method = 'ESEWA'
                payment.payment_status = 'COMPLETED'
                payment.transaction_id = 'DEV_' + str(uuid.uuid4())[:8]
                payment.save()
                
                # Update pet status if this is a pet adoption payment
                if payment.pet:
                    payment.pet.status = 'ADOPTED'
                    payment.pet.save()
                
                messages.success(request, 'Development Mode: Payment simulated successfully!')
                return redirect(f"{reverse('payment:payment_success')}?payment_id={payment.id}")
            
            # For v2 API, we need to decode the data parameter
            if data:
                try:
                    # Decode base64 data and parse JSON
                    decoded_data = json.loads(base64.b64decode(data).decode('utf-8'))
                    print(f"Decoded eSewa data: {decoded_data}")
                    
                    # Check if the status is COMPLETE (case insensitive check)
                    status = decoded_data.get('status', '')
                    if status.upper() != 'COMPLETE':
                        error_msg = f"Payment not completed. Status: {status}"
                        payment.mark_as_failed(error_msg)
                        messages.error(request, error_msg)
                        return redirect('payment:payment_failed')
                    
                    # Get the transaction code
                    refId = decoded_data.get('transaction_code', '')
                    
                    # Payment successful
                    payment.payment_method = 'ESEWA'
                    payment.payment_status = 'COMPLETED'
                    payment.transaction_id = refId
                    payment.save()
                    
                    # Update pet status if this is a pet adoption payment
                    if payment.pet:
                        payment.pet.status = 'ADOPTED'
                        payment.pet.save()
                    
                    messages.success(request, 'Payment successful!')
                    return redirect(f"{reverse('payment:payment_success')}?payment_id={payment.id}")
                except Exception as e:
                    error_msg = f'Error decoding eSewa data: {str(e)}'
                    payment.mark_as_failed(error_msg)
                    messages.error(request, error_msg)
                    return redirect('payment:payment_failed')
            else:
                # Fallback to old verification method if data is not provided
                amt = request.GET.get('amt')
                refId = request.GET.get('refId')  # eSewa's transaction reference
                
                # Verify the payment with eSewa
                url = "https://uat.esewa.com.np/epay/transrec"
                payload = {
                    'amt': amt,
                    'scd': settings.ESEWA_MERCHANT_CODE,
                    'rid': refId,
                    'pid': oid,
                }
                
                # Log the verification request for debugging
                print(f"eSewa verification request: {payload}")
                
                try:
                    response = requests.post(url, payload, timeout=10)
                    print(f"eSewa verification response: {response.text}")
                    
                    if 'Success' in response.text:
                        # Payment successful
                        payment.payment_method = 'ESEWA'
                        payment.payment_status = 'COMPLETED'
                        payment.transaction_id = refId
                        payment.save()
                        
                        # Update pet status if this is a pet adoption payment
                        if payment.pet:
                            payment.pet.status = 'ADOPTED'
                            payment.pet.save()
                        
                        messages.success(request, 'Payment successful!')
                        return redirect('payment:payment_success')
                    else:
                        # Payment failed
                        error_msg = 'Payment verification failed'
                        if 'Duplicate' in response.text:
                            error_msg = 'Duplicate transaction detected. Please try again with a new payment.'
                        payment.mark_as_failed(error_msg)
                        messages.error(request, error_msg)
                        return redirect('payment:payment_failed')
                except requests.RequestException as req_err:
                    # Handle request errors (timeout, connection issues, etc.)
                    error_msg = f'Connection error during payment verification: {str(req_err)}'
                    payment.mark_as_failed(error_msg)
                    messages.error(request, 'Payment verification failed due to connection issues. Please try again.')
                    return redirect('payment:payment_failed')
                
        except Exception as e:
            print(f"eSewa verification error: {str(e)}")
            messages.error(request, 'An error occurred during payment verification')
            if 'payment' in locals():
                payment.mark_as_failed(str(e))
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('payment:payment_failed')

    return redirect('payment:payment_failed')

@csrf_exempt
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    oid = request.GET.get('oid')  # Get oid from eSewa callback
    
    # Try to find the payment by ID or transaction_uuid
    payment = None
    try:
        if payment_id:
            payment = get_object_or_404(Payment, id=payment_id)
        elif oid:
            payment = get_object_or_404(Payment, transaction_uuid=oid)
        
        # If payment found but not marked as completed, update it
        if payment and payment.payment_status != 'COMPLETED':
            payment.payment_method = 'ESEWA'
            payment.payment_status = 'COMPLETED'
            payment.save()
            
            # Update pet status if this is a pet adoption payment
            if payment.pet and payment.pet.status != 'ADOPTED':
                payment.pet.status = 'ADOPTED'
                payment.pet.save()
        
        # In development mode, use the development template
        if settings.DEBUG and payment:
            return render(request, 'payment/dev_payment_success.html', {
                'payment': payment
            })
        
        # In production, use the regular template
        context = {'payment': payment} if payment else {}
        return render(request, 'payment/success.html', context)
        
    except Exception as e:
        messages.error(request, f'Error retrieving payment details: {str(e)}')
        return render(request, 'payment/success.html')

@csrf_exempt
def payment_failed(request):
    context = {}
    
    # Check if we have an oid (transaction_uuid) from eSewa
    oid = request.GET.get('oid')
    payment_id = request.GET.get('payment_id')
    error_code = request.GET.get('error')
    
    # Set specific error messages based on error code
    if error_code:
        if error_code == 'no_pending_payment':
            context['error_message'] = 'No pending payment was found for your account. Please try again with a new payment.'
        elif error_code == 'find_payment_error':
            context['error_message'] = 'There was an error finding your payment. Please try again.'
        elif error_code == 'not_logged_in':
            context['error_message'] = 'You must be logged in to complete this payment. Please log in and try again.'
    
    # Try to find the payment by transaction_uuid or payment_id
    payment = None
    try:
        # First try to find by transaction_uuid
        if oid:
            try:
                payment = Payment.objects.get(transaction_uuid=oid)
            except Payment.DoesNotExist:
                # If not found by transaction_uuid, log this for debugging
                print(f"Payment with transaction_uuid={oid} not found")
                # If user is logged in, try to find any pending payment
                if request.user.is_authenticated and not error_code:
                    pending_payment = Payment.objects.filter(
                        user=request.user, 
                        payment_status='PENDING'
                    ).order_by('-created_at').first()
                    
                    if pending_payment:
                        payment = pending_payment
                        context['note'] = 'We found a pending payment in your account.'
        
        # If not found by transaction_uuid, try by payment_id
        if not payment and payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
            except Payment.DoesNotExist:
                # If not found by payment_id, log this for debugging
                print(f"Payment with id={payment_id} not found")
                pass
        
        # If payment was found by either method
        if payment:
            if payment.error_message:
                context['error_message'] = context.get('error_message', payment.error_message)
            else:
                # Mark as failed if not already
                if payment.payment_status != 'FAILED':
                    payment.mark_as_failed('Payment was cancelled or failed')
                context['error_message'] = context.get('error_message', 'Your payment was not completed.')
            context['payment'] = payment
        elif not context.get('error_message'):
            # No payment found by either method and no error message set yet
            context['error_message'] = 'Payment record not found. Please try again with a new payment.'
    except Exception as e:
        # Log any unexpected errors
        print(f"Error in payment_failed view: {str(e)}")
        context['error_message'] = f'An error occurred while processing your payment: {str(e)}'
    
    return render(request, 'payment/failed.html', context)
