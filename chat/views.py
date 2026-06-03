from django.shortcuts import render, redirect, get_object_or_404
from .models import Message, Direct, Call
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Profile
from .forms import DirectForm

User = get_user_model()


@login_required(login_url='login')
def chat_page(request):
    if request.method == "POST":
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(text=text, user=request.user)
        return redirect('global_chat')

    messages = Message.objects.filter(is_delete=False).order_by("-writed_at")
    return render(request, 'chat/chats.html', {"messages": messages})


@login_required(login_url='login')
def like(request, pk):
    ms = get_object_or_404(Message, pk=pk)
    if request.user not in ms.likes.all():
        ms.likes.add(request.user)
    else:
        ms.likes.remove(request.user)
    return redirect('global_chat')


@login_required(login_url='login')
def dizlike(request, pk):
    ms = get_object_or_404(Message, pk=pk)
    if request.user not in ms.dizlikes.all():
        ms.dizlikes.add(request.user)
    else:
        ms.dizlikes.remove(request.user)
    return redirect('global_chat')


class MessageDeleteView(LoginRequiredMixin, generic.DeleteView):
    """
    Исправлено: URL использует <int:pk>, поэтому убраны slug_field / slug_url_kwarg.
    Мягкое удаление — ставим is_delete=True вместо реального удаления из БД.
    """
    model = Message
    template_name = 'chat/message_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return obj

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_delete = True
        obj.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('global_chat')


@login_required(login_url='login')
def profile_view(request, username):
    profile = get_object_or_404(User, username=username)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required(login_url='login')
def send_message(request, pk):
    ptn = get_object_or_404(User, pk=pk)
    Profile.objects.get_or_create(user=request.user)
    Profile.objects.get_or_create(user=ptn)

    if ptn == request.user:
        return redirect('show_messages')

    if request.method == 'POST':
        text = request.POST.get("text", "").strip()
        photo = request.FILES.get("photo")
        voice = request.FILES.get("voice")

        if text or photo or voice:
            Direct.objects.create(
                sender=request.user,
                receiner=ptn,
                text=text,       
                photo=photo,
                voice=voice,
            )

        return redirect('send_message', ptn.pk)

    messages = Direct.objects.filter(
        Q(sender=request.user, receiner=ptn) |
        Q(sender=ptn, receiner=request.user)
    ).select_related(
        "sender", "receiner",
        "sender__profile", "receiner__profile"
    ).order_by("created_at")

    messages.filter(receiner=request.user, is_readed=False).update(is_readed=True)

    return render(request, 'chat/send_message.html', {
        "messages": messages,
        "profile": ptn,
    })


@login_required(login_url='login')
def show_messages(request):
    user = request.user

    users = User.objects.filter(
        Q(send_messages__receiner=user) |
        Q(received_messages__sender=user)
    ).exclude(id=user.id).distinct()

    dialogs = []
    for companion in users:
        last_message = Direct.objects.filter(
            Q(sender=user, receiner=companion) |
            Q(sender=companion, receiner=user)
        ).order_by('-created_at').first()

        dialogs.append({
            "user": companion,
            "last_message": last_message,
        })

    dialogs.sort(
        key=lambda x: x["last_message"].created_at if x["last_message"] else 0,
        reverse=True,
    )

    return render(request, "chat/show_messages.html", {"dialogs": dialogs})


@login_required(login_url='login')
def delete_chat(request, pk):
    other_user = get_object_or_404(User, pk=pk)
    Direct.objects.filter(
        Q(sender=request.user, receiner=other_user) |
        Q(sender=other_user, receiner=request.user)
    ).delete()
    return redirect('show_messages')


@login_required(login_url='login')
def start_video_call(request, user_id):
    receiver = get_object_or_404(User, pk=user_id)
    
    if receiver == request.user:
        return redirect('show_messages')
    
    # Создаем новый вызов
    call = Call.objects.create(
        caller=request.user,
        receiver=receiver,
        call_type='video',
        status='pending'
    )
    
    return redirect('video_call', call_id=call.id)


@login_required(login_url='login')
def video_call(request, call_id):
    call = get_object_or_404(Call, pk=call_id)
    
    # Проверяем, что пользователь участвует в вызове
    if call.caller != request.user and call.receiver != request.user:
        return redirect('show_messages')
    
    # Если вызов уже завершен, перенаправляем
    if call.status == 'ended':
        return redirect('show_messages')
    
    # Если пользователь - получатель и вызов в ожидании, принимаем его
    if call.receiver == request.user and call.status == 'pending':
        call.status = 'accepted'
        call.save()
    
    return render(request, 'chat/video_call.html', {
        'call': call,
        'is_caller': call.caller == request.user,
    })