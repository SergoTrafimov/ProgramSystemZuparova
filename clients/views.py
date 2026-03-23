from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from projects.models import Project
from .models import Feedback
from .forms import FeedbackForm

@login_required
def project_feedback(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.project = project
            feedback.from_client = True
            feedback.save()
            messages.success(request, 'Сообщение отправлено.')
            return redirect('project_feedback', project_id=project.id)
    else:
        form = FeedbackForm()
    feedbacks = Feedback.objects.filter(project=project).order_by('-created_at')
    return render(request, 'clients/feedback.html', {'project': project, 'form': form, 'feedbacks': feedbacks})