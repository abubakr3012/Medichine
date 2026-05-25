from django.shortcuts import render,redirect,get_object_or_404
from .models import Message
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
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


@login_required(login_url='/login/')
def like(request,pk):
    ms=Message.objects.get(pk=pk)
    ms.likes+=1
    ms.save()

    return redirect('global_chat')

@login_required(login_url='/login/')
def dizlike(request,pk):
    ms=Message.objects.get(pk=pk)
    ms.dizlikes+=1
    ms.save()
    return redirect('global_chat')

@login_required(login_url='/login/')
def delete_message(request,pk):
    ms=get_object_or_404(Message,pk=pk)
    if request.user==ms.user:
        ms.delete()
    return redirect('global_chat')