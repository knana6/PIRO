from django.shortcuts import render, redirect
from .models import Post

# Create your views here.

# def hello_world(request) :
# 	#return HttpResponse("Hello World")
#     return render(request, "hello.html")

def posts_list(request):
    posts = Post.objects.all()
    context = {
        "posts": posts
    }
    return render(request, "posts_list.html", context)

def posts_read(request, pk):
    posts= Post.objects.get(id=pk)
    context = {
        "posts": posts
    }
    return render(request, "posts_read.html", context)

def posts_create(request):
    if request.method == "POST":
            Post.objects.create(
                title = request.POST["title"],
                user = request.POST["user"],
                content = request.POST["content"],
            )   
            return redirect("posts:posts_list")
    return render(request, "posts_create.html")

def post_update(request,pk):
    post = Post.objects.get(id=pk)

    if request.method == "POST":
        post.title = request.POST["title"]
        post.user = request.POST["user"]
        post.content = request.POST["content"]
        post.save()

        return redirect("posts:read", pk=pk)
     
    context = {"post": post}
    return render(request, "posts_update.html", context)


def posts_delete(request, pk):
    if request.method == "POST":
        post = Post.objects.get(id=pk)
        post.delete()
    return redirect("posts:posts_list")