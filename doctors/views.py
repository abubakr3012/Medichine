from django.shortcuts import render,redirect,get_object_or_404
from .models import DoctorProfile
from django.db.models import Q,Max,Count

def show_all_doctors(request):
    profile=DoctorProfile.objects.select_related('user')
    q=request.GET.get('q','').strip()
    if q:
        profile=profile.filter(
            Q(user__name__icontains=q)|
            Q(speciality__icontains=q)|
            Q(city__icontains=q)
        )
    stats=profile.aggregate(
        all_patients=Count('id'),
        more_patients=Max('user')
    )
    return render(request,'doctors/doctors.html',{"Doctors":profile,"stats":stats})
