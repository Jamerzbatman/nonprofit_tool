from django import forms
from .models import WebSite, Tag


class WebSiteForm(forms.ModelForm):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}))

    class Meta:
        model = WebSite
        fields = ['name', 'description', 'tags']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        return name.lower().replace(' ', '_')

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if tags_str:
            return [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        return []
