from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...',
            'aria-label': 'Search',
        })
    )
    
    def clean_query(self):
        query = self.cleaned_data.get('query', '').strip()
        if not query:
            raise forms.ValidationError("Please enter a search term.")
        return query
