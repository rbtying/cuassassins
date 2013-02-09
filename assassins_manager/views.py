# Create your views here.
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from assassins_manager.services import render_with_metadata
from models import *

def about(request):
    return render_with_metadata(request, 'about/about.html')
