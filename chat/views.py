from django.shortcuts import render,redirect,get_object_or_404
from .models import Message,Direct
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from accounts.models import Profile

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
    messages = Message.objects.all().order_by("-writed_at").filter(is_delete=False)

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

# @login_required(login_url='login')
# def delete_message(request,pk):
#     ms=get_object_or_404(Message,pk=pk)
#     if request.user==ms.user:
#         ms.delete()
#     return redirect('global_chat')

class MessageDeleteView(LoginRequiredMixin,generic.DeleteView):
    model=Message
    slug_field='slug'
    slug_url_kwarg='slug'
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_delete = True
        obj.save()
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('global_chat')


@login_required(login_url='login')
def profile_view(request,username):
    profile=get_object_or_404(User,username=username)
    return render(request,'accounts/profile.html',{'profile':profile})

@login_required(login_url='login')
def send_message(request,pk):
    ptn=get_object_or_404(User,pk=pk)
    Profile.objects.get_or_create(user=request.user)
    Profile.objects.get_or_create(user=ptn)

    if ptn == request.user:
        return redirect('show_messages')

    if request.method == 'POST':
        text = request.POST.get("text", "").strip()
        if text:
            Direct.objects.create(
                sender=request.user,
                receiner=ptn,
                text=text
            )
        return redirect('send_message',ptn.pk)

    message=Direct.objects.filter(
        Q(sender=request.user, receiner=ptn) |
        Q(sender=ptn, receiner=request.user)
    ).select_related("sender", "receiner", "sender__profile", "receiner__profile").order_by("created_at")
    message.filter(receiner=request.user, is_readed=False).update(is_readed=True)
    return render(request,'chat/send_message.html',{"messages":message,"profile":ptn})

@login_required(login_url='login')
def show_messages(request):
    user=request.user
    users=list(User.objects.filter(
        Q(send_messages__receiner=user)|
        Q(received_messages__sender=user)
    ).distinct())
    for companion in users:
        profile, _ = Profile.objects.get_or_create(user=companion)
        companion.profile = profile
    return render(request,'chat/show_messages.html',{"users":users})

@login_required(login_url='login')
def delete_chat(request, pk):
    other_user = get_object_or_404(User, pk=pk)

    Direct.objects.filter(
        Q(sender=request.user, receiner=other_user) |
        Q(sender=other_user, receiner=request.user)
    ).delete()

    return redirect('show_messages')
