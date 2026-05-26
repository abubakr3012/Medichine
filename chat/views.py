from django.shortcuts import render,redirect,get_object_or_404
from .models import Message,Direct
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q


User=get_user_model()

@login_required(login_url='login')
def chat_page(request):
    if request.method=="POST":
        text=request.POST['text']

        if text:
            Message.objects.create(
                text=text,
                user=request.user
            )
        return redirect('global_chat')
    messages = Message.objects.all().order_by("-writed_at")

    return render(request,'chat/chats.html',{"messages":messages})

@login_required(login_url='login')
def like(request,pk):
    ms=get_object_or_404(Message,pk=pk)
    if request.user not in ms.likes.all():
        ms.likes.add(request.user)
    else:
        ms.likes.remove(request.user)
    return redirect('global_chat')

@login_required(login_url='login')
def dizlike(request,pk):
    ms=Message.objects.get(pk=pk)
    if request.user not in ms.dizlikes.all():
        ms.dizlikes.add(request.user)
    else:
        ms.dizlikes.remove(request.user)
    return redirect('global_chat')

@login_required(login_url='login')
def delete_message(request,pk):
    ms=get_object_or_404(Message,pk=pk)
    if request.user==ms.user:
        ms.delete()
    return redirect('global_chat')

def profile_view(request,username):
    profile=get_object_or_404(User,username=username)
    return render(request,'accounts/profile.html',{'profile':profile})

@login_required(login_url='login')
def send_message(request,pk):
    ptn=get_object_or_404(User,pk=pk)
    if request.method == 'POST':
        Direct.objects.create(
            sender=request.user,
            receiner=ptn,
            text=request.POST.get("text")
        )
        return redirect('send_message',ptn.pk)
    return render(request,'chat/send_message.html',{"receiver":ptn})
    
@login_required(login_url='login')
def chat(request,pk):
    ptn=get_object_or_404(User,pk=pk)

    message=Direct.objects.filter(
        Q(sender=request.user,receiner=ptn)|
        Q(sender=ptn,receiner=request.user)
    ).order_by("created_at")
    return render(request,'chat/send_message.html',{"messages":message})