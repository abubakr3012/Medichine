from django.shortcuts import render,redirect,get_object_or_404
from .models import Appointment
from doctors.models import DoctorProfile

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

def show_appointment(request):
    appointment=Appointment.objects.all()
    return render(request,'appoinments/show_appointment.html',{"appointments":appointment})

def delete_appointment(request,pk):
    appointment=get_object_or_404(Appointment,pk=pk)
    if request.user == appointment.user:
        if request.method == 'POST':
            appointment.delete()
    return redirect('appointments')
    