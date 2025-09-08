# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.models import User
# from django.contrib import messages
# from rest_framework_simplejwt.tokens import RefreshToken
# from .forms import RegisterForm, LoginForm


# def register_view(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data["password"])
#             user.save()
#             messages.success(request, "Registration successful.")
#             login(request, user)
#             return redirect('list')
#     else:
#         form = RegisterForm()
#     return render(request, './Users/register.html', {'form': form})


# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)  # Add this: sets request.user for the session
#                 token = RefreshToken.for_user(user)
#                 request.session['access'] = str(token.access_token)
#                 request.session['refresh'] = str(token)
#                 messages.success(request, 'Logged in successfully.')
#                 return redirect('list')
#             else:
#                 messages.error(request, "Invalid username or password.")
#     else:
#         form = LoginForm()
#     return render(request, './Users/login.html', {'form': form})


# def logout_view(request):
#     # Accept POST from header form; also allow GET to be forgiving.
#     if request.method == "POST" or request.method == "GET":
#         # optionally blacklist the refresh token if present
#         refresh = request.session.get('refresh')
#         if refresh:
#             try:
#                 token = RefreshToken(refresh)
#                 token.blacklist()
#             except Exception:
#                 pass
#         logout(request)  # Add this: properly logs out and clears session
#         messages.success(request, "Logged out successfully.")
#     return redirect('login')


# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
# from rest_framework.authtoken.models import Token
# from .serializer import RegisterSerializer
# from django.contrib.auth import logout

# from django.urls import reverse_lazy



# class SignupView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request):
#         return render(request, "Users/register.html")

#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()  # Ensure serializer.save() hashes password
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key}, status=status.HTTP_201_CREATED)


# class SigninView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request):
#         return render(request, "Users/login.html")

#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(request, username=username, password=password)
#         if not user:
#             return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response({'token': token.key}, status=status.HTTP_200_OK)

# class LogoutView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         # remove token if it exists
#         try:
#             request.user.auth_token.delete()
#         except Exception:
#             pass
#         # clear session
#         logout(request)
#         # instruct client to redirect to home
#         return Response(
#             {'success': 'Logged out'},
#             status=status.HTTP_302_FOUND,
#             headers={'Location': reverse_lazy('home')}
#         )

#     def get(self, request):
#         # allow GET to behave the same for convenience
#         return self.post(request)

# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages
# from django.urls import reverse
# from .forms import RegisterForm, LoginForm

# def signup_view(request):
#     if request.method == "POST":
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data["password"])
#             user.save()
#             messages.success(request, "Registration successful.")
#             # Auto-login after signup (optional)
#             user = authenticate(request, username=user.username, password=form.cleaned_data["password"])
#             if user:
#                 login(request, user)
#             next_url = request.GET.get("next") or reverse("home")
#             return redirect(next_url)
#     else:
#         form = RegisterForm()
#     return render(request, "Users/register.html", {"form": form})

# def signin_view(request):
#     next_url = request.GET.get("next")  # supports ?next=/where/to/go
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             user = authenticate(request,
#                                 username=form.cleaned_data["username"],
#                                 password=form.cleaned_data["password"])
#             if user:
#                 login(request, user)
#                 return redirect(next_url or "home")
#             messages.error(request, "Invalid credentials.")
#     else:
#         form = LoginForm()
#     return render(request, "Users/login.html", {"form": form, "next": next_url})

# def signout_view(request):
#     logout(request)
#     messages.success(request, "Logged out.")
#     return redirect("login")

# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
# from django.contrib.auth import logout as django_logout
# from django.urls import reverse
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from rest_framework.authtoken.models import Token
# from .forms import RegisterForm, LoginForm

# class SignupView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request):
#         form = RegisterForm()
#         return render(request, "users/register.html", {"form": form})

#     def post(self, request):
#         form = RegisterForm(request.POST)
#         if not form.is_valid():
#             return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)
#         username = form.cleaned_data["username"]
#         email = form.cleaned_data.get("email") or ""
#         password = form.cleaned_data["password"]
#         if User.objects.filter(username=username).exists():
#             return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
#         user = User.objects.create_user(username=username, email=email, password=password)
#         token, _ = Token.objects.get_or_create(user=user)
#         # Return JSON so template JS can redirect as needed.
#         return Response({"token": token.key}, status=status.HTTP_201_CREATED)

# class SigninView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request):
#         form = LoginForm()
#         next_url = request.GET.get("next", "")
#         return render(request, "users/login.html", {"form": form, "next": next_url})

#     def post(self, request):
#         form = LoginForm(request.POST)
#         if not form.is_valid():
#             return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)
#         username = form.cleaned_data["username"]
#         password = form.cleaned_data["password"]
#         user = authenticate(request, username=username, password=password)
#         if not user:
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
#         token, _ = Token.objects.get_or_create(user=user)
#         # Return token; frontend JS will redirect to next/home.
#         return Response({"token": token.key}, status=status.HTTP_200_OK)

# class LogoutView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         # If an authenticated user made the request with a token, delete it.
#         if request.user and request.user.is_authenticated:
#             try:
#                 request.user.auth_token.delete()
#             except Exception:
#                 pass
#         django_logout(request)
#         # Server-side redirect for convenience (no JSON here).
#         return redirect("login")

#     def get(self, request):
#         return self.post(request)

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
            messages.success(request, 'Account created!')
            return redirect('list')
    else:
        form = SignupForm()
    # ensure we render the form for GET and for invalid POST
    return render(request, 'Users/register.html', {'form': form})


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
