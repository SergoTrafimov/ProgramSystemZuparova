from django import forms
from .models import Feedback, ClientMessage, MessageReply

class MessageReplyForm(forms.ModelForm):
    class Meta:
        model = MessageReply
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']

class ClientMessageForm(forms.ModelForm):
    class Meta:
        model = ClientMessage
        fields = ['subject', 'message']