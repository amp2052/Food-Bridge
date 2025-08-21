from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import RegistrationForm
import random
from django.core.mail import send_mail
from .models import CustomUser, Donation, Campaign
from .models import Donation, FoodRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import FoodDonationForm
from .models import FoodDonation
from .models import NGOProfile
from .forms import  NGOUserForm,NGOProfileForm
from app.models import Campaign, Donation
from django.contrib.auth import authenticate, login
from .models import Donation, FoodDonation
from .models import UserProfile


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            otp = str(random.randint(100000, 999999))
            request.session['user_data'] = form.cleaned_data
            request.session['otp'] = otp

            send_mail(
                'OTP verification',
                f'Your OTP is {otp}',
                'amp2052@gmail.com',
                [form.cleaned_data['email']]
            )
            return redirect('verify_otp')
    else:
        form = RegistrationForm()
    return render(request, 'app/register.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        if request.POST['otp'] == request.session.get('otp'):
            data = request.session.get('user_data')
            user = CustomUser.objects.create_user(
                email=data['email'],
                role=data['role'],
                password=data['password']
            )
            messages.success(request, "Account is created ! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP")
    return render(request, 'app/verify_otp.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, email=request.POST['email'], password=request.POST['password'])
        if user:
            login(request, user)
            request.session['access_token'] = get_tokens_for_user(user)['access']

            if user.role == 'donor':
                return redirect('donor_dashboard')
            elif user.role == 'ngo':
                return redirect('ngo_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'app/login.html')


@login_required
def dashboard(request):
    return render(request, 'app/dashboard.html', {'role': request.user.role})

@login_required
def donor_dashboard(request):
    if request.method == 'POST':
        form = FoodDonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.save()
            return redirect('donor_dashboard')  
    else:
        form = FoodDonationForm()

    donations = FoodDonation.objects.filter(donor=request.user).order_by('-timestamp')
    return render(request, 'app/donor_dashboard.html', {'form': form, 'donations': donations})

from django.contrib.auth.decorators import login_required
from .models import FoodDonation

@login_required
def ngo_dashboard(request):
    available_donations = FoodDonation.objects.filter(
        status='pending',
        claimed_by__isnull=True
    ).select_related('donor')

    pending_requests = FoodDonation.objects.filter(
    status='pending',
    claimed_by__isnull=True
)

    accepted_requests = FoodDonation.objects.filter(
        status='accepted',
        claimed_by=request.user
    )

    return render(request, 'app/ngo_dashboard.html', {
        'available_donations': available_donations,
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
    })
 
@login_required
@user_passes_test(lambda user: user.is_authenticated and user.role == 'admin')
def admin_dashboard(request):
    total_donations = Donation.objects.count()
    total_ngos = CustomUser.objects.filter(role='ngo').count()
    active_claims = Campaign.objects.filter(status='active').count()  
    recent_activity = [
        "Admin approved a donation campaign.",
        "User Alice registered as a donor.",
        "NGO GreenHope submitted a claim.",
        "Donation received from user Bob.",
        "Campaign updated by NGO WaterRelief."
    ]
    return render(request, 'app/admin_dashboard.html', {
        'user': request.user,
        'total_donations': total_donations,
        'total_ngos': total_ngos,
        'active_claims': active_claims,
        'recent_activity': recent_activity,
    })


def logout_view(request):
    logout(request)
    return redirect('login')


def forgot_password(request):
    if request.method == 'POST':
        try:
            user = CustomUser.objects.get(email=request.POST['email'])
            otp = str(random.randint(100000, 999999))
            request.session['forgot_email'] = user.email
            request.session['forgot_otp'] = otp
            send_mail('Password Reset OTP', f'Your OTP is:{otp}', 'amp2052@gmail.com', [user.email])
            return redirect('verify_forgot_otp')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Email not found')
    return render(request, 'app/forgot_password.html')


def verify_forgot_otp(request):
    if request.method == 'POST':
        if request.POST['otp'] == request.session.get('forgot_otp'):
            if request.POST['new_password1'] == request.POST['new_password2']:
                user = CustomUser.objects.get(email=request.session['forgot_email'])
                user.set_password(request.POST['new_password1'])
                user.save()
                messages.success(request, "Password reset successful")
                return redirect('login')
            else:
                messages.error(request, "Password do not match")
        else:
            messages.error(request, "Invalid OTP")
    return render(request, 'app/verify_forgot_otp.html')


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@user_passes_test(is_admin)
def user_management(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'app/user_management.html', {'users': users})


@user_passes_test(is_admin)
def system_stats(request):
    total_users = CustomUser.objects.count()
    total_donations = Donation.objects.count()
    total_campaigns = Campaign.objects.count()

    stats = {
        'total_users': total_users,
        'total_donations': total_donations,
        'total_campaigns': total_campaigns,
    }

    return render(request, 'app/system_stats.html', {'stats': stats})


@user_passes_test(is_admin)
def audit_logs(request):
    logs = [
        {"timestamp": "2025-07-10 12:00", "action": "Donor JohnDoe made a donation."},
        {"timestamp": "2025-07-10 11:30", "action": "NGO SaveEarth created a campaign."},
        {"timestamp": "2025-07-10 10:45", "action": "Admin approved a new NGO account."},
    ]
    return render(request, 'app/audit_logs.html', {'logs': logs})


def about_us(request):
    return render(request, 'app/about_us.html')

@login_required
def post_donation(request):
    if request.method == 'POST':
        form = FoodDonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.status = 'pending'
            donation.save()
            messages.success(request, "Donation submitted successfully!")
            return redirect('donor_dashboard')
    else:
        form = FoodDonationForm()
    return render(request, 'app/post_donation.html', {'form': form})
from django.conf import settings

@login_required
def claim_donation(request, donation_id):
    try:
        donation = FoodDonation.objects.get(id=donation_id, status='pending')
        donation.status = 'accepted'
        donation.claimed_by = request.user
        donation.save()

        FoodRequest.objects.create(
            ngo=request.user,
            donation=donation,
            status='accepted'
        )

        # Send email to the donor
        if donation.donor and donation.donor.email:
            donor_name = donation.donor.email
            ngo_name = request.user.email

            subject = 'Your Food Donation Has Been Claimed'
            message = (
                f"Dear {donor_name},\n\n"
                f"Your food donation ({donation.food_type}, {donation.quantity} {donation.unit}) "
                f"has been claimed by NGO.\n\n"
                f"They will coordinate with you shortly for pickup at:\n"
                f"{donation.pickup_address}\n\n"
                "Thank you for your generous contribution!\n\n"
                "Best regards,\n"
                "Food Bridge Team"
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[donation.donor.email],
                fail_silently=True
            )

        messages.success(request, "Donation claimed successfully and donor notified via email!")
    except FoodDonation.DoesNotExist:
        messages.error(request, "Donation not found or already claimed.")
    return redirect('ngo_dashboard')

@login_required
def donor_profile(request):
    profile = None
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = None

    # Combine first name and last name
    full_name = f"{request.user.first_name} {request.user.last_name}".strip()

    context = {
        'profile': profile,
        'name': full_name if full_name else request.user.email,  
    }
    return render(request, 'app/donor_profile.html', context)

@login_required
def ngo_profile(request):
    try:
        profile = NGOProfile.objects.get(user=request.user)
    except NGOProfile.DoesNotExist:
        return redirect('create_ngo_profile')
    return render(request, 'app/ngo_profile.html', {'ngo_profile': profile})


@login_required
def create_ngo_profile(request):
    if request.method == 'POST':
        form = NGOProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('ngo_profile')
    else:
        form = NGOProfileForm()
    return render(request, 'app/create_ngo_profile.html', {'form': form})

@login_required
def edit_ngo_profile(request):
    user = request.user
    try:
        ngo_profile = NGOProfile.objects.get(user=user)
    except NGOProfile.DoesNotExist:
        return redirect('create_ngo_profile')

    if request.method == 'POST':
        user_form = NGOUserForm(request.POST, instance=user)
        profile_form = NGOProfileForm(request.POST, instance=ngo_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('ngo_profile')
    else:
        user_form = NGOUserForm(instance=user)
        profile_form = NGOProfileForm(instance=ngo_profile)

    return render(request, 'app/edit_ngo_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

def ngo_history(request):
    deliveries = FoodRequest.objects.all()  
    context = {'deliveries': deliveries}
    return render(request, 'app/ngo_history.html', context)

def landing_page(request):
    return render(request, 'app/landing_page.html')


def contact_us(request):
    return render(request, 'app/contact_us.html')

def faq(request):
    return render(request, 'app/faq.html')
def privacy(request):
    return render(request, 'app/privacy.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from app.models import FoodDonation, FoodRequest, Donation, CustomUser
from datetime import datetime

@login_required
@user_passes_test(lambda user: user.role == 'admin')

def dashboard(request):
    food_posts = FoodDonation.objects.all()

    food_type = request.GET.get('food_type')
    location = request.GET.get('location')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if food_type == '':
        food_type = None
    if location == '':
        location = None

    if food_type:
        food_posts = food_posts.filter(food_type__iexact=food_type.strip())

    if location:
        food_posts = food_posts.filter(pickup_address__icontains=location.strip())

    if start_date:
        try:
            parsed_start_date = datetime.strptime(start_date, "%m/%d/%Y").date()
            food_posts = food_posts.filter(pickup_deadline__date__gte=parsed_start_date)
        except ValueError:
            print("Invalid start date format")

    # if end_date:
    #     food_posts = food_posts.filter(timestamp__date__lte=end_date)

    total_food_saved = food_posts.aggregate(total=Sum('quantity'))['total'] or 0
    total_ngos = CustomUser.objects.filter(role='ngo').count()
    total_food_posts = food_posts.count()
    total_amount_donated = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0

    recent_food_posts = food_posts.order_by('-timestamp')[:2]
    recent_deliveries = FoodRequest.objects.select_related('donation', 'ngo').order_by('-timestamp')[:2]
    # recent_donations = Donation.objects.select_related('donor', 'campaign').order_by('-donated_at')[:3]

    context = {
        'selected_food_type': food_type or '',
        'selected_location': location or '',
        'start_date': start_date or '',
        'end_date': end_date or '',

        'total_food_saved': total_food_saved,
        'total_ngos': total_ngos,
        'total_food_posts': total_food_posts,
        'total_amount_donated': total_amount_donated,

        'recent_food_posts': recent_food_posts,
        'recent_deliveries': recent_deliveries,
        # 'recent_donations': recent_donations,
        'show_logout': True,
    }

    return render(request, 'app/admin_dashboard.html', context)

@login_required
@user_passes_test(lambda user: user.role == 'admin')
def all_food_posts(request):
    food_donations = FoodDonation.objects.order_by('-timestamp')
    return render(request, 'app/all_food_posts.html', {
        'food_donations': food_donations
    })

@login_required
@user_passes_test(lambda user: user.role == 'admin')
def all_deliveries(request):
    deliveries = FoodRequest.objects.select_related('donation', 'ngo').order_by('-timestamp')
    return render(request, 'app/all_deliveries.html', {'deliveries': deliveries})

# @login_required
# @user_passes_test(lambda user: user.role == 'admin')
# def all_donations(request):
#     donations = Donation.objects.select_related('donor', 'campaign').order_by('-donated_at')
#     return render(request, 'adminDApp/all_donations.html', {'donations': donations})
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa

from .models import FoodDonation  # change according to your project

@login_required
def admin_pdf_report(request):
    # Data to include in the PDF
    donations = FoodDonation.objects.all()

    # Load the PDF template
    template = get_template('app/admin_report.html')
    html = template.render({'donations': donations, 'admin_user': request.user})

    # Create a response object with PDF content type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="admin_report.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response
