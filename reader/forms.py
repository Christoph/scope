from django import forms
from django.forms import ModelForm
import datetime
from captcha.fields import CaptchaField
from reader.models import RSSFeed, User_Reader

class SourceForm(ModelForm):
    class Meta:
        model = RSSFeed
        fields = ['name','url']
        labels = {
            'name': 'Feed name',
            'url': 'Feed url',
        }


class ReaderForm(ModelForm):
    class Meta:
        model = User_Reader
        fields = ['feeds', 'no_output_articles']
        labels = {
            'feeds': 'Current Feeds',
            'no_output_articles': '# Output Articles',
        }
        # widgets = {
        #     'feeds': 
        # }
    def __init__(self, *args, **kwargs):
        super(ReaderForm, self).__init__(*args, **kwargs)
        self.fields['feeds'].choices = [(i.url,i.name) for i in RSSFeed.objects.all()]

    feeds = forms.MultipleChoiceField(label= 'Select sources',widget=forms.SelectMultiple(attrs= {'id': 'sources'}),
                                              choices=(), required=False)
    # no_output_articles = forms.IntegerField()