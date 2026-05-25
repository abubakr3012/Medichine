from django.shortcuts import render,redirect,get_object_or_404
from .models import DoctorProfile
from django.db.models import Q,Max,Count

def show_all_doctors(request):
    profile=DoctorProfile.objects.select_related('user').filter(user__role='doctor')
    q=request.GET.get('q','').strip()
    if q:
        profile = profile.filter(
            Q(user__username__icontains=q) |
            Q(speciality__icontains=q) |
            Q(city__icontains=q)
        )
    stats=profile.aggregate(
        all_patients=Count('id')
    )
    return render(request,'doctors/doctors.html',{"doctors":profile,"stats":stats})
