from django.shortcuts import render,redirect,get_object_or_404
from .models import Appointment
from doctors.models import DoctorProfile
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required(login_url='login')
def create_appointment(request,pk):
    doctor=get_object_or_404(DoctorProfile,pk=pk)
    if request.method=='POST':
        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            date=request.POST.get('date')
        )
        return redirect('doctors_list')
    return render(request,'appoinments/appoinments.html',{"doctor":doctor})

@login_required(login_url='login')
def show_appointment(request):
    if request.user.is_superuser:
        appointment=Appointment.objects.select_related('patient', 'doctor__user').all()
    else:
        appointment=Appointment.objects.select_related('patient', 'doctor__user').filter(
            Q(patient=request.user) | Q(doctor__user=request.user)
        )
    return render(request,'appoinments/show_appointment.html',{"appointments":appointment})

@login_required(login_url='login')
def delete_appointment(request,pk):
    appointment=get_object_or_404(Appointment,pk=pk)
    can_delete = (
        request.user.is_superuser or
        request.user == appointment.patient or
        request.user == appointment.doctor.user
    )
    if request.method == 'POST' and can_delete:
        appointment.delete()
    return redirect('appointments')
    
