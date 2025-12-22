from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg

from . import models
from .forms import OpinionForm

# Definición de views
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def destinations(request):
    all_destinations = models.Destination.objects.all()
    return render(request, 'destinations.html', {'destinations': all_destinations})


class DestinationDetailView(generic.DetailView):
    template_name = 'destination_detail.html'
    model = models.Destination
    context_object_name = 'destination'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        destination = self.get_object()
        context['avg_rating'] = destination.opinions.aggregate(avg=Avg('rating'))['avg']
        context['opinions_count'] = destination.opinions.count()
        return context


class CruiseDetailView(generic.DetailView):
    template_name = 'cruise_detail.html'
    model = models.Cruise
    context_object_name = 'cruise'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cruise = self.get_object()
        context['avg_rating'] = cruise.opinions.aggregate(avg=Avg('rating'))['avg']
        context['opinions_count'] = cruise.opinions.count()
        return context


class InfoRequestCreate(SuccessMessageMixin, generic.CreateView):
    template_name = 'info_request_create.html'
    model = models.InfoRequest
    fields = ['name', 'email', 'cruise', 'notes']
    success_url = reverse_lazy('index')
    success_message = 'Thank you, %(name)s! We will email you when we have more information about %(cruise)s!'

    def form_valid(self, form):
        response = super().form_valid(form)
        info_request = self.object

        subject = 'Nueva solicitud de información ~ ReleCloud'
        message = f"""
Se ha recibido una nueva solicitud de información:

Nombre: {info_request.name}
Email: {info_request.email}
Crucero: {info_request.cruise}
Notas: {info_request.notes}
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['admin@relecloud.com'],
        )
        return response


@login_required
def create_opinion(request):
    """
    Permite crear una opinión SOLO a usuarios logueados
    y SOLO sobre destinos/cruceros que estén en UserTravelRecord del usuario.
    """
    if request.method == "POST":
        form = OpinionForm(request.user, request.POST)
        if form.is_valid():
            opinion = form.save(commit=False)

            # Seguridad extra: comprobar que realmente lo ha "viajado"
            if opinion.destination:
                ok = models.UserTravelRecord.objects.filter(
                    user=request.user, destination=opinion.destination
                ).exists()
                if not ok:
                    messages.error(request, "No puedes valorar un destino que no hayas comprado/viajado.")
                    return redirect('destinations')

            if opinion.cruise:
                ok = models.UserTravelRecord.objects.filter(
                    user=request.user, cruise=opinion.cruise
                ).exists()
                if not ok:
                    messages.error(request, "No puedes valorar un crucero que no hayas comprado/viajado.")
                    return redirect('destinations')

            opinion.save()
            messages.success(request, "¡Gracias! Tu valoración se ha guardado.")
            return redirect('destinations')
    else:
        form = OpinionForm(request.user)

    return render(request, "opinion_create.html", {"form": form})
