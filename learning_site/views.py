from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView

from . import forms


#  This is my new class based view
class HelloWorldView(View):
    def get(self, request):
        return HttpResponse("Hello World")

class HomeView(TemplateView):
    template_name = 'home.html'


#  These are function based views
def suggestion_view(request):
    form = forms.SuggestionForm()
    if request.method == 'POST':
        form = forms.SuggestionForm(request.POST)
        if form.is_valid():
            send_mail(
                'Suggestion from {}'.format(form.cleaned_data['name']),
                form.cleaned_data['suggestion'],
                '{name} <{email}>'.format(**form.cleaned_data),
                ['kenneth@teamtreehouse.com']
            )
            messages.add_message(request, messages.SUCCESS,
                                 'Thanks for your suggestion!')
            return HttpResponseRedirect(reverse('suggestion'))
    return render(request, 'suggestion_form.html', {'form': form})