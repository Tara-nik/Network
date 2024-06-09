from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models.fields.related import ManyToManyField
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone

from django import forms

from .models import User, Post
# Create your views here.



def index(request):
    return render(request, "network/index.html")
def login_view(request):
    if request.method == "POST":
        print(request.POST)

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)


        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("all_posts"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("all_posts"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })


        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse('all_posts'))
    else:
        return render(request, "network/register.html")


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'cols': 80, 'rows': 5 }),
        }
@login_required
def new_post(request):
    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.writer = request.user
            new_post.timestamp = timezone.now()
            new_post.save()
            return redirect('all_posts')
    else:
        form = NewPostForm()

    return render(request, 'network/index.html', {'form': form})


def all_posts(request):
    post_list = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(post_list, 10)

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
    }

    return render(request, 'network/index.html', context)


@login_required
def following_posts(request):
    following_users = request.user.following.all()
    following_posts = Post.objects.filter(writer__in=following_users).order_by('-timestamp')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(following_posts, 10)

    try:
        following_posts = paginator.page(page)
    except PageNotAnInteger:
        following_posts = paginator.page(1)
    except EmptyPage:
        following_posts = paginator.page(paginator.num_pages)

    return render(request, "network/following_post.html", {
        'following_posts': following_posts,
    })



@login_required
@csrf_exempt
def profile(request, username):
    viewed_user = get_object_or_404(User, username=username)
    current_user = request.user

    is_own_profile = current_user == viewed_user
    if current_user in viewed_user.followers.all():
        is_following = True
        print(viewed_user.followers.all())
        print(current_user)
        print(viewed_user)
    else:
        is_following = False

    if request.method == 'POST' and 'follow_toggle' in request.POST:
        if is_following:
            current_user.following.remove(viewed_user)
            viewed_user.followers.remove(current_user)

            is_following = False
            response_data = {'toggle': 'success', 'button_text': 'Follow'}
        else:
            current_user.following.add(viewed_user)
            viewed_user.following.add(current_user)
            is_following = True
            response_data = {'status': 'success', 'button_text': 'Unfollow'}
        return JsonResponse(response_data)

    context = {
        'viewed_user': viewed_user,
        'current_user': current_user,
        'is_own_profile': is_own_profile,
        'followers_count': viewed_user.followers.count(),
        'following_count': viewed_user.following.count(),
        'user_posts': Post.objects.filter(writer=viewed_user).order_by('-timestamp'),
        'is_following': is_following,
    }

    return render(request, 'network/profile.html', context)


@login_required
@csrf_exempt
def follow(request, username):
    if request.method == 'POST':
        user_to_follow = User.objects.get(username=username)

        if user_to_follow in request.user.following.all():
            request.user.following.remove(user_to_follow)
            user_to_follow.followers.remove(request.user)
            button_text = 'Follow'
        else:
            request.user.following.add(user_to_follow)
            user_to_follow.followers.add(request.user)
            button_text = 'Unfollow'

        return JsonResponse({'status': 'success', 'button_text': button_text})


@login_required
@csrf_exempt
def unfollow(request, username):
    try:
        user_to_unfollow = User.objects.get(username=username)
        request.user.following.remove(user_to_unfollow)
        user_to_unfollow.followers.remove(request.user)
        response_data = {'status': 'success'}
    except User.DoesNotExist:
        response_data = {'status': 'error', 'message': 'User does not exist'}
        return JsonResponse(response_data, status=400)
    except Exception as e:
        response_data = {'status': 'error', 'message': str(e)}
        return JsonResponse(response_data, status=500)

    print(f"Unfollow response data: {response_data}")
    return JsonResponse(response_data)

@require_POST
def like_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": post.likes.count()})




class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.writer:
        return redirect('all_posts')

    if request.method == 'POST':
        form = PostEditForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "message": "Post edited successfully"})
        else:
            return JsonResponse({"success": False, "errors": form.errors})
    else:
        form = PostEditForm(instance=post)

    return render(request, 'network/index.html', {'form': form, 'post': post})


