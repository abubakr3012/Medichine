from django.shortcuts import render,redirect,get_object_or_404
from .models import Appointment
from doctors.models import DoctorProfile
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .tasks import send_sms
from django.utils.dateparse import parse_datetime
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone


class AppointmentCreateView(LoginRequiredMixin,generic.CreateView):
    model=Appointment
    fields=['date']
    success_url=reverse_lazy('appointments')
    template_name='appoinments/appoinments.html'

    def form_valid(self, form):
        doctor=get_object_or_404(DoctorProfile,pk=self.kwargs['pk'])
        form.instance.doctor=doctor
        form.instance.patient=self.request.user

        return super().form_valid(form)
    
class AppointmentListView(LoginRequiredMixin,generic.ListView):
    model=Appointment
    template_name='appoinments/show_appointment.html'

    def get_queryset(self):
        Appointment.objects.filter(
            status='pending',
            date__lte=timezone.now()
        ).update(status='approved')

        return Appointment.objects.select_related('doctor').filter(is_deleted=False)

class AppointmentDeleteView(LoginRequiredMixin,generic.DeleteView):
    
    model=Appointment
    slug_field='slug'
    slug_url_kwarg='slug'
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('appointments')

class AppointmentUpdateView(LoginRequiredMixin,generic.UpdateView):
    model=Appointment
    fields=['date','status']
    success_url=reverse_lazy('appointments')
    slug_field='slug'
    slug_url_kwarg='slug'
    template_name='appoinments/update_appointment.html'

@login_required(login_url='login')
def appointment_create(request, pk):

    doctor = DoctorProfile.objects.get(id=pk)

    if request.method == 'POST':

        appointment = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=request.POST.get('date')
        )

        send_sms(
            "+992003993162",
            f"Вы записаны к врачу {doctor} на {appointment.date}"
        )

        return redirect('my_appointments')
    
