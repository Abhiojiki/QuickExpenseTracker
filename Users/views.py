
"""Views for user signup, login and logout.

This module contains small function-based views used by templates. Each view
follows Django's standard calling convention (request -> HttpResponse) and
keeps side effects minimal. These docstrings explain inputs/outputs and
important behavior for maintainers.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignupForm, LoginForm
from django.contrib.auth.decorators import login_required
# Users/views.py
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect


def signup_view(request):
    """Render and process the signup form.

    Inputs:
    - request: HttpRequest

    Behavior:
    - GET: renders `Users/register.html` with an empty `SignupForm`.
    - POST: validates `SignupForm`; on success creates the user (password is
      hashed via `set_password`) and redirects to the transaction `list` view.

    Returns:
    - HttpResponse rendering the form for GET or invalid POST, or a
      redirect HttpResponse on successful signup.
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
             # Auto-login so user is not bounced back to login page
            login(request, user)
            messages.success(request, 'Account created!')
            return redirect('list')
    else:
        form = SignupForm()
    # ensure we render the form for GET and for invalid POST
    return render(request, 'Users/register.html', {'form': form})

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    """Render and process the login form.

    Supports optional `next` query parameter to redirect after successful
    authentication.

    Inputs:
    - request: HttpRequest (GET or POST)

    Behavior:
    - GET: renders `Users/login.html` with an empty `LoginForm`.
    - POST: validates `LoginForm`, attempts authentication and logs the user in
      (calling Django's `login`) on success. On authentication failure the form
      is re-rendered with error messages.

    Returns:
    - HttpResponse rendering the login template, or a redirect on successful
      login.
    """
    # handle both GET and POST and always return an HttpResponse
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect(next_url or 'list')
            messages.error(request, 'Invalid credentials')
        # fall through to render the form with errors
    else:
        form = LoginForm()

    return render(request, 'Users/login.html', {'form': form, 'next': next_url})


@login_required
def logout_view(request):
    """Log the current user out and redirect to the login page.

    Inputs:
    - request: HttpRequest

    Returns:
    - HttpResponse redirecting to the named URL `login`.
    """
    logout(request)
    # redirect to login page after logout
    return redirect('login')
