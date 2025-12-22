from django import forms
from .models import Opinion, Cruise, Destination, UserTravelRecord

# Definición de forms
class OpinionForm(forms.ModelForm):
    choice = forms.ChoiceField(
        choices=[('destination', 'Destino'), ('cruise', 'Crucero')],
        widget=forms.RadioSelect,
        label="¿Qué quieres valorar?"
    )

    cruise = forms.ModelChoiceField(
        queryset=Cruise.objects.none(),
        required=False,
        label="Selecciona un crucero"
    )

    destination = forms.ModelChoiceField(
        queryset=Destination.objects.none(),
        required=False,
        label="Selecciona un destino"
    )

    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Valoración",
        required=True
    )

    class Meta:
        model = Opinion
        fields = ['choice', 'cruise', 'destination', 'rating']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        visited_destinations = UserTravelRecord.objects.filter(
            user=user,
            destination__isnull=False
        ).values_list('destination', flat=True).distinct()

        visited_cruises = UserTravelRecord.objects.filter(
            user=user,
            cruise__isnull=False
        ).values_list('cruise', flat=True).distinct()

        self.fields['destination'].queryset = Destination.objects.filter(id__in=visited_destinations)
        self.fields['cruise'].queryset = Cruise.objects.filter(id__in=visited_cruises)

    def clean(self):
        cleaned_data = super().clean()
        choice = cleaned_data.get('choice')
        cruise = cleaned_data.get('cruise')
        destination = cleaned_data.get('destination')

        if choice == 'cruise' and not cruise:
            raise forms.ValidationError("Debes seleccionar un crucero.")
        if choice == 'destination' and not destination:
            raise forms.ValidationError("Debes seleccionar un destino.")

        # Limpiar el otro campo para no guardar los dos
        if choice == 'cruise':
            cleaned_data['destination'] = None
        if choice == 'destination':
            cleaned_data['cruise'] = None

        return cleaned_data
