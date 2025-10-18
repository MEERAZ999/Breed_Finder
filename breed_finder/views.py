from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import json
import requests
from verify_email.email_handler import send_verification_email
from .forms import CustomUserCreationForm, PetForm, UserUpdateForm, ProfileUpdateForm
from .models import CustomUser, Pet, UserProfile
from payment.models import Payment
from .tokens import account_activation_token

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Import settings and check if we're in development mode
                from django.conf import settings
                
                if settings.DEBUG:
                    # In development mode, create the user directly and show verification link
                    user = form.save(commit=False)
                    user.is_active = False  # User will be inactive until verified
                    user.save()
                    
                    # Generate verification link manually
                    from django.contrib.sites.shortcuts import get_current_site
                    from django.utils.http import urlsafe_base64_encode
                    from django.utils.encoding import force_bytes
                    from django.urls import reverse
                    from .tokens import account_activation_token
                    
                    current_site = get_current_site(request)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = account_activation_token.make_token(user)
                    verification_link = f"{settings.EMAIL_PAGE_DOMAIN}{reverse('breed_finder:activate', kwargs={'uidb64': uid, 'token': token})}"
                    
                    # Show the verification link on a development page
                    return render(request, 'breed_finder/dev_email_verification.html', {
                        'email': user.email,
                        'verification_link': verification_link
                    })
                else:
                    # In production, use the normal email verification flow
                    # send_verification_email returns either an inactive_user object or False
                    result = send_verification_email(request, form)
                    
                    # Check if we got a valid user object back
                    if result and hasattr(result, 'email'):
                        return render(request, 'breed_finder/email_sent.html', {
                            'email': result.email
                        })
                    else:
                        # This handles the case when send_verification_email returns False
                        messages.error(request, 'Failed to send verification email. Please try again.')
                        return render(request, 'breed_finder/register.html', {'form': form})
            except Exception as e:
                messages.error(request, f'Error sending verification email: {str(e)}')
                return render(request, 'breed_finder/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'breed_finder/register.html', {'form': form})

@login_required
def landing_page(request):
    # Get only the 6 most recent available pets for the homepage
    pets = Pet.objects.filter(status='AVAILABLE').order_by('-created_at')[:6]
    # Count total available pets to determine if we need the 'View All' button
    total_available_pets = Pet.objects.filter(status='AVAILABLE').count()
    return render(request, 'breed_finder/landing.html', {
        'pets': pets,
        'show_view_all': total_available_pets > 6
    })

def chatbot(request):
    # Get the total count of available dogs
    dog_count = Pet.objects.filter(status='AVAILABLE').count()
    return render(request, 'breed_finder/chatbot.html', {
        'dog_count': dog_count
    })

@csrf_exempt
def ollama_proxy(request):
    if request.method == 'POST':
        try:
            # Forward the request to Ollama API
            ollama_url = 'http://localhost:11434/api/generate'
            data = json.loads(request.body)
            
            # Make the request to Ollama
            response = requests.post(ollama_url, json=data)
            
            # Return the response from Ollama
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@user_passes_test(lambda u: u.is_staff)
def add_pet(request):
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save()
            messages.success(request, 'Pet added successfully!')
            return redirect('payment:payment_page', pet_id=pet.id)
    else:
        form = PetForm()
    return render(request, 'breed_finder/pet_form.html', {'form': form, 'action': 'Add'})

@user_passes_test(lambda u: u.is_staff)
def edit_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        form = PetForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pet updated successfully!')
            return redirect('breed_finder:pet_list')
    else:
        form = PetForm(instance=pet)
    return render(request, 'breed_finder/pet_form.html', {'form': form, 'action': 'Edit'})

@user_passes_test(lambda u: u.is_staff)
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    if request.method == 'POST':
        pet.delete()
        messages.success(request, 'Pet deleted successfully!')
        return redirect('breed_finder:pet_list')
    return render(request, 'breed_finder/pet_confirm_delete.html', {'pet': pet})

@login_required
def pet_list(request):
    # Get search query from request
    search_query = request.GET.get('search', '')
    
    # Start with all pets
    pets = Pet.objects.all()
    
    # Apply search filter if a query is provided
    if search_query:
        # Case-insensitive search on breed field
        pets = pets.filter(breed__icontains=search_query)
    
    # Order by creation date (newest first)
    pets = pets.order_by('-created_at')
    
    # Get breed counts for each pet
    for pet in pets:
        pet.breed_total = Pet.objects.filter(breed__iexact=pet.breed).count()
        pet.breed_available = Pet.objects.filter(breed__iexact=pet.breed, status='AVAILABLE').count()
    
    return render(request, 'breed_finder/pet_list.html', {
        'pets': pets,
        'search_query': search_query
    })

@login_required
def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    
    # Count total and available dogs of this breed
    breed_total = Pet.objects.filter(breed__iexact=pet.breed).count()
    breed_available = Pet.objects.filter(breed__iexact=pet.breed, status='AVAILABLE').count()
    
    if request.method == 'POST':
        if pet.status == 'AVAILABLE':
            return redirect('payment:payment_page', pet_id=pet.id)
        elif pet.status == 'ADOPTED':
            messages.info(request, f'{pet.name} has already been adopted.')
        elif pet.status == 'PENDING':
            messages.warning(request, f'Adoption for {pet.name} is pending.')
        else:
            messages.error(request, f'{pet.name} is not available for adoption at this time.')
    
    return render(request, 'breed_finder/pet_detail.html', {
        'pet': pet,
        'breed_total': breed_total,
        'breed_available': breed_available
    })

@login_required
def user_profile(request):
    # Get user's adoptions (completed payments)
    adoptions = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'breed_finder/user_profile.html', {
        'adoptions': adoptions
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('breed_finder:user_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'breed_finder/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # Verify that the email is from Gmail
        if not user.email.endswith('@gmail.com'):
            messages.error(request, 'Only Gmail accounts are allowed for registration.')
            return render(request, 'breed_finder/email/verification_failed.html')
            
        user.is_active = True
        user.is_email_verified = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('breed_finder:landing')
    else:
        return render(request, 'breed_finder/email/verification_failed.html')
