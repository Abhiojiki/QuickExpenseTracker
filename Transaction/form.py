"""Forms used by the Transaction app.

Provides `TransactionForm` used by Create/Update views and a small
`CategoryForm` for potential category CRUD. Forms include validation for
common domain rules (amount > 0, date not in the future).
"""

from django import forms
from django.utils import timezone

from .models import Transaction, Category


class TransactionFilterForm(forms.Form):
    """Simple filter form used on the transaction list page.

    Fields:
    - start_date, end_date: optional date range
    - category: optional category id to filter by
    """
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": "w-full px-4 py-2 border rounded"}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date", "class": "w-full px-4 py-2 border rounded"}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="All categories", widget=forms.Select(attrs={"class": "w-full px-4 py-2 border rounded"}))



class TransactionForm(forms.ModelForm):
    """Form contract

    Inputs:
    - transaction_type: 'income' or 'expense' (used to filter categories)
    - amount: float > 0
    - category: FK to Category
    - date: date (not in the future)
    - image: optional ImageField
    - description: text

    Output: cleaned_data matching Transaction fields. On save(), views set `user` on the instance.
    Error modes: raises ValidationError for invalid amount or future date.
    """
    
    # Add a non-model type field for filtering categories
    TRANSACTION_TYPES = (("expense", "Expense"), ("income", "Income"))
    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPES,
        required=True,
        initial="expense",
        label="Transaction Type",
        widget=forms.RadioSelect(attrs={"class": "form-radio h-4 w-4 text-blue-600"})
    )

    class Meta:
        model = Transaction
        fields = ["amount", "category", "date", "image", "description"]
        widgets = {
            "amount": forms.NumberInput(attrs={
                "step": "1", "min": "0", "class": "focus:ring-blue-500 focus:border-blue-500 block w-full pl-3 pr-12 sm:text-sm border-gray-300 rounded-md"
            }),
            "category": forms.Select(attrs={"class": "mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 rounded-md"}),
            
            "date": forms.DateInput(attrs={"type": "date", "class": "shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"}),
            
            "image": forms.ClearableFileInput(attrs={"class": "block w-full text-sm text-gray-600 file-input", "accept": "image/*"}),
            
            "description": forms.Textarea(attrs={"rows": 3, "class": "shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border border-gray-300 rounded-md"}),
        }
        help_texts = {
            "image": "Optional: upload a receipt or related image.",
            "description": "Brief note about the transaction.",
        }

    def __init__(self, *args, user=None, **kwargs):
        """Accept optional `user` to allow later filtering or behaviour if needed.

        We don't set the Transaction.user here because views set it in form_valid.
        """
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Initialize transaction_type based on the category if we're editing an existing transaction
        instance = kwargs.get('instance')
        if instance and instance.category:
            self.initial['transaction_type'] = instance.category.type
            
        # Add dynamic filtering of categories based on transaction type
        self.fields['category'].help_text = "Select a category matching the transaction type"
        
        # JavaScript to filter categories based on transaction type will be added in the template

    def clean(self):
        """Validate form data including cross-field validation."""
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        
        if transaction_type and category and category.type != transaction_type:
            self.add_error('category', f"Please select a {transaction_type} category.")
            
        return cleaned_data
        
    def clean_amount(self):
        amt = self.cleaned_data.get("amount")
        if amt is None:
            return amt
        if amt <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amt

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date and date > timezone.localdate():
            raise forms.ValidationError("Date cannot be in the future.")
        return date

    def clean_image(self):
        """Validate uploaded image size to limit to 200 KB to reduce S3 costs.

        Returns the file if valid or raises ValidationError otherwise.
        """
        image = self.cleaned_data.get('image')
        if image:
            max_size = 200 * 1024  # 200 KB
            # Some storage backends provide size attribute on the file
            size = getattr(image, 'size', None)
            if size is not None and size > max_size:
                raise forms.ValidationError("Image file too large (max 200 KB). Please compress or choose a smaller image.")
        return image


class CategoryForm(forms.ModelForm):
    """Small form for Category if you later need to create/edit categories via views.

    Not used by the current views, provided for completeness.
    """

    class Meta:
        model = Category
        fields = ["name", "type"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "type": forms.Select(attrs={"class": "select"}),
        }
