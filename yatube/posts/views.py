from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow
from .utils import pagination

User = get_user_model()


def index(request):
    posts = Post.objects.all()
    page_obj = pagination(request, posts)

    context = {
        'page_obj': page_obj,
        'title': 'Главная страница Yatube',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(request, posts)
    title = group.title
    context = {
        'page_obj': page_obj,
        'group': group,
        'title': title
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    posts_count = author.posts.count
    page_obj = pagination(request, posts)
    following = Follow.objects.filter(user__username=user, author=author).exists()
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    posts_count = author.posts.count
    title = f'Пост {post.text[:30]}'
    comment_form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'posts_count': posts_count,
        'post': post,
        'title': title,
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)
    else:
        return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user
    )
    context = {
        'page_obj': pagination(request, post_list)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            author=author,
            user=request.user
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow_obj = Follow.objects.filter(
        user=request.user.id, author=author.id
    )
    if request.user != author and follow_obj.exists():
        follow_obj.delete()
    return redirect('posts:profile', username)
