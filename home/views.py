from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
import random
# Create your views here.

def home_view(request):
    template = loader.get_template('about.html')
    return HttpResponse(template.render())

def cv_view(request):
    template = loader.get_template('cv.html')
    return HttpResponse(template.render())

def experience_view(request):
    template = loader.get_template('experience.html')
    return HttpResponse(template.render())

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        user_answer = request.POST.get("captcha_answer")
        correct_answer = request.POST.get("correct_captcha")

        if not user_answer or int(user_answer) != int (correct_answer):
            messages.error(request, "Dit svar er desværre ikke rigtigt, prøv igen =)")
            return redirect("contact")

        send_mail(
            subject=f"Du har modtaget en besked fra {name} igennem dit online-cv.",
            message=f"Navn: {name}\nEmail: {email}\n\n Besked: {message}",
            from_email="lysell.nielsen@gmail.com",
            recipient_list=["lysell.nielsen@gmail.com"],
            fail_silently=False,
        )
        messages.success(request, "Beskeden er sendt =)")
        return redirect("contact")

    return render(request, "contact.html")
