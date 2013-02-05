from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from forms import ColumbiaUserCreationForm

def register(request):
    if request.method == 'POST':
        form = ColumbiaUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return login(request)
    else:
        form = ColumbiaUserCreationForm()
    return render_to_response('registration/register.html', {'form': form},
            context_instance=RequestContext(request))

def post_login(sender, user, **kwargs):
    if not user.columbiauserprofile is None:
        user.columbiauserprofile.ldap_update()

from django.contrib.auth.signals import user_logged_in
user_logged_in.connect(post_login)

def whoami(request):
    return HttpResponse("You are logged in as %s" % request.user.username)
