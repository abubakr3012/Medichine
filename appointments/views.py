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

    def dispatch(self, request, *args, **kwargs):
        # Только пациенты могут создавать записи
        if request.user.role != 'patient':
            return redirect('appointments')
        return super().dispatch(request, *args, **kwargs)

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

        user = self.request.user
        
        # Безопасность: по умолчанию показываем только свои записи
        base_queryset = Appointment.objects.select_related('doctor', 'patient').filter(
            is_deleted=False
        )
        
        # Пациенты видят только свои записи
        if user.role == 'patient':
            return base_queryset.filter(patient=user)
        
        # Врачи видят только записи к ним
        elif user.role == 'doctor':
            try:
                doctor_profile = user.doctorprofile
                return base_queryset.filter(doctor=doctor_profile)
            except (DoctorProfile.DoesNotExist, AttributeError):
                return Appointment.objects.none()
        
        # Админы видят все записи
        elif user.role == 'admin':
            return base_queryset
        
        # Если роль не определена - показываем только свои записи для безопасности
        return base_queryset.filter(patient=user)

class AppointmentDeleteView(LoginRequiredMixin,generic.DeleteView):
    
    model=Appointment
    slug_field='slug'
    slug_url_kwarg='slug'
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(is_deleted=False)
        
        # Пациенты могут удалять только свои записи
        if user.role == 'patient':
            return queryset.filter(patient=user)
        
        # Врачи могут удалять только записи к ним
        elif user.role == 'doctor':
            try:
                doctor_profile = user.doctorprofile
                return queryset.filter(doctor=doctor_profile)
            except (DoctorProfile.DoesNotExist, AttributeError):
                return Appointment.objects.none()
        
        # Админы могут удалять все записи
        return queryset
    
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
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(is_deleted=False)
        
        # Пациенты могут редактировать только свои записи
        if user.role == 'patient':
            return queryset.filter(patient=user)
        
        # Врачи могут редактировать только записи к ним
        elif user.role == 'doctor':
            try:
                doctor_profile = user.doctorprofile
                return queryset.filter(doctor=doctor_profile)
            except (DoctorProfile.DoesNotExist, AttributeError):
                return Appointment.objects.none()
        
        # Админы могут редактировать все записи
        return queryset

@login_required(login_url='login')
def appointment_create(request, pk):
    # Только пациенты могут создавать записи
    if request.user.role != 'patient':
        return redirect('appointments')

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
    
