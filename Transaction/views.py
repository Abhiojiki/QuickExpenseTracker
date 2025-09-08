
"""Views for Transaction app.

This module exposes class-based views used by the transaction UI. Each view
is documented with inputs/outputs and any non-obvious side effects. Views
consistently filter queryset by the currently authenticated user to avoid
information leakage.
"""

from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required   
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Transaction  # Import the models we defined
from django.contrib.auth.decorators import login_required
from .form import TransactionForm
from .form import TransactionFilterForm

# Updated views: these use TransactionForm and pass the request.user into the form kwargs.


class homepageView(TemplateView):
    """Simple homepage view for landing content.

    Renders the template `transaction/homepage.html`. No special context is
    provided.
    """
    template_name = 'transaction/homepage.html'


class TransactionListView(LoginRequiredMixin, ListView):
    """List transactions belonging to the current user.

    Attributes:
    - model: Transaction
    - template_name: template used to render the list
    - context_object_name: name used in template for the queryset

    The `get_queryset` method filters results to the authenticated user.
    """
    model = Transaction
    template_name = 'transaction/transaction_list.html'
    context_object_name = 'transactions'
    login_url = 'login'

    def get_queryset(self):
        """Return only transactions owned by the current user."""
        qs = Transaction.objects.filter(user=self.request.user).select_related('category')

        # Apply filters from GET parameters (start_date, end_date, category)
        start = self.request.GET.get('start_date')
        end = self.request.GET.get('end_date')
        category = self.request.GET.get('category')

        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if category:
            try:
                cat_id = int(category)
                qs = qs.filter(category_id=cat_id)
            except (ValueError, TypeError):
                pass

        return qs

    def get_context_data(self, **kwargs):
        """Add total_balance to context for display."""
        context = super().get_context_data(**kwargs)
        transactions = context.get('transactions', [])

        income = sum(
            t.amount for t in transactions
            if getattr(t, 'category', None) and t.category.type == 'income'
        )
        expense = sum(
            t.amount for t in transactions
            if getattr(t, 'category', None) and t.category.type == 'expense'
        )

        context['total_balance'] = income - expense
        context['total_income'] = income
        context['total_expense'] = expense

        # Add filter form populated from GET and list of categories for the filters partial
        context['filter_form'] = TransactionFilterForm(self.request.GET or None)
        context['all_categories'] = Category.objects.all()

        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """Create a new Transaction for the logged-in user.

    The view injects `user` into the form kwargs and sets `form.instance.user`
    in `form_valid` to ensure the saved Transaction references the authenticated
    user.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction/transaction_form.html'
    success_url = reverse_lazy('list')

    def get_form_kwargs(self):
        """Add the current user to the form kwargs for potential use in form logic."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Assign the logged-in user to the Transaction before saving."""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Provide template flags used to control form rendering."""
        context = super().get_context_data(**kwargs)
        context['show_delete_button'] = False
        context['edit_transaction'] = False
        
        # Add categories by type for JavaScript filtering
        context['income_categories'] = Category.objects.filter(type='income')
        context['expense_categories'] = Category.objects.filter(type='expense')
        
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """Show a single Transaction, ensuring it belongs to the user."""
    model = Transaction
    template_name = 'transaction/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        """Limit visible objects to those owned by the request user."""
        return super().get_queryset().filter(user=self.request.user)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Edit an existing Transaction owned by the user.

    Ensures the form receives the `user` and that only objects owned by the
    user can be updated.
    """
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction/transaction_form.html'
    success_url = reverse_lazy('list')

    def get_queryset(self):
        """Limit editable objects to those owned by the request user."""
        return super().get_queryset().filter(user=self.request.user)

    def get_form_kwargs(self):
        """Pass the request user to the form constructor."""
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        """Add template flags for rendering edit/delete controls."""
        context = super().get_context_data(**kwargs)
        context['show_delete_button'] = True
        context['edit_transaction'] = True
        
        # Add categories by type for JavaScript filtering
        context['income_categories'] = Category.objects.filter(type='income')
        context['expense_categories'] = Category.objects.filter(type='expense')
        
        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a Transaction that belongs to the authenticated user."""
    model = Transaction
    template_name = 'transaction/transaction_confirm_delete.html'
    success_url = reverse_lazy('list')

    def get_queryset(self):
        """Return only objects owned by the request user so other users cannot delete them."""
        return super().get_queryset().filter(user=self.request.user)

