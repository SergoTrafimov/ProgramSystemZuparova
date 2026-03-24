from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from projects.models import Project
from .models import Feedback, ClientMessage
from .forms import FeedbackForm, ClientMessageForm, MessageReplyForm

@login_required
def view_client_message(request, message_id):
    message = get_object_or_404(ClientMessage, id=message_id, created_by=request.user)
    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.message = message
            reply.author = request.user
            reply.save()
            messages.success(request, 'Сообщение отправлено.')
            return redirect('view_client_message', message_id=message.id)
    else:
        form = MessageReplyForm()
    return render(request, 'clients/view_message.html', {
        'message': message,
        'replies': message.replies.all().order_by('created_at'),
        'form': form,
    })

@login_required
def client_dashboard(request):
    if request.user.profile.role != 'client':
        return redirect('index')
    messages_list = ClientMessage.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'clients/client_dashboard.html', {'messages': messages_list})

@login_required
def create_client_message(request):
    if request.method == 'POST':
        form = ClientMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.created_by = request.user
            msg.save()
            messages.success(request, 'Ваше сообщение отправлено.')
            return redirect('client_dashboard')
    else:
        form = ClientMessageForm()
    return render(request, 'clients/create_message.html', {'form': form})

@login_required
def project_feedback(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user.profile.role != 'admin' and project.organization != request.user.profile.organization:
        messages.error(request, 'Доступ запрещён.')
        return redirect('index')
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.project = project
            if request.user.profile.role in ['analyst', 'curator', 'admin']:
                feedback.from_client = False
            else:
                feedback.from_client = True
            feedback.save()
            messages.success(request, 'Сообщение отправлено.')
            return redirect('project_feedback', project_id=project.id)
    else:
        form = FeedbackForm()
    feedbacks = Feedback.objects.filter(project=project).order_by('-created_at')
    return render(request, 'clients/feedback.html', {
        'project': project,
        'form': form,
        'feedbacks': feedbacks,
    })