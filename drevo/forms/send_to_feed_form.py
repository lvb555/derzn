from django import forms

from drevo.models.feed_messages import FeedMessage

class SendToFeedForm(forms.Form):
    """
        Форма для отправки сообщения в Ленту знаний
    """
    text = forms.CharField(max_length=511, required = True)
    class Meta:
        model = FeedMessage
        fields = ('recipient', 'label', 'znanie', 'text', )