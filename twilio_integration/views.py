# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from assassins_manager.services import render_with_metadata
from assassins_manager.models import *
from twilio_integration.models import *
from twilio_integration.forms import *
from services import send_text

@login_required
def send_code(request):
    try:
        p = PhoneNumber.objects.get(user=request.user)
    except PhoneNumber.DoesNotExist:
        raise Http404

    send_text(p.phone_number, p.verify_code)

    return HttpResponseRedirect(reverse('twilio_integration.views.verify_code'))

@login_required
def verify_code(request):
    try:
        p = PhoneNumber.objects.get(user=request.user)
    except PhoneNumber.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = VerifyPhone(request.POST)
        form.set_code(p.verify_code)
        if form.is_valid():
            p.is_verified = True;
            p.save()
            return HttpResponseRedirect(reverse('twilio_integration.views.edit_phone'))
    else:
        form = VerifyPhone()
        form.set_code(p.verify_code)

    return render(request, 'verify.html', {'form': form, 'number':p,})

@login_required
def edit_phone(request):
    try:
        p = PhoneNumber.objects.get(user=request.user)
    except PhoneNumber.DoesNotExist:
        p = PhoneNumber(user=request.user)
        p.phone_number = ''
        p.is_verified = False
        p.generate_code(commit=True)

    if request.method == 'POST':
        form = EditPhone(request.POST, instance=p)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('changed'):
                user.is_verified = False
                user.generate_code(commit=False)
            user.save()
    else:
        form = EditPhone(instance=p)
    return render(request, 'phone.html', {'form': form, 'formtitle': 'Enter a phone number', 'number': p,})
