from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from  .models import Post, Category, Comment
from .forms import PostForm, EditForm, CommentForm
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

def LikeView(request, pk):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return HttpResponseRedirect(reverse('article-detail',args=[str(pk)]))


class HomeView(ListView):
    model= Post
    paginate_by = 2
    template_name = 'home.html'
    ordering = ['-post_date']


    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        return context

def CategoryListView(request):
    cat_menu_list = Category.objects.all()
    return render(request, 'category_list.html', {'cat_menu_list':cat_menu_list})

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def CategoryView(request, cats):
    category_posts = Post.objects.filter(category=cats.replace('-', ' '))
    paginator = Paginator(category_posts, 3)
    page_number = request.GET.get('page')
    try:
        category_posts = paginator.page(page_number)
    except PageNotAnInteger:
        category_posts = paginator.page(1)
    except EmptyPage:
        category_posts = paginator.page(paginator.num_pages)
    return render(request, 'categories.html', {'cats':cats.title().replace('-', ' '), 'category_posts':category_posts})

class ArticleDetailView(DetailView):
    model = Post
    template_name = 'article_details.html'

    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)

        stuff = get_object_or_404(Post, id=self.kwargs['pk'])
        total_likes = stuff.total_likes()

        liked = False
        if stuff.likes.filter(id=self.request.user.id).exists():
            liked =True

        context["cat_menu"] = cat_menu
        context["total_likes"] = total_likes
        context["liked"] = liked
        return context

class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'add_post.html'
    


class AddCommentView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'add_comment.html'
    # fields = '__all__'
    def form_valid(self, form):
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)

    success_url = reverse_lazy('home')

class AddCategoryView(CreateView):
    model = Category
    # form_class = PostForm
    template_name = 'add_category.html'
    fields = '__all__'

class UpdatePostView(UpdateView):
    model = Post
    form_class = EditForm
    template_name = 'update_post.html'
    # fields = ['title', 'title_tag', 'body']

class DeletePostView(DeleteView):
    model = Post
    template_name = 'delete_post.html'
    success_url = reverse_lazy('home')

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        articles = Post.objects.filter(title__contains=searched)
        return render(request, 'search.html',{'searched':searched, 'articles':articles})
    
    else:
        return render(request, 'search.html', {})


# from django.conf import settings
# def display_video(request,vid=None):
#     if vid is None:
#         return HttpResponse("No Video")
#     video_name = vid +" .mp4 "
#     video_url = settings.MEDIA_URL+video_name
#     return render(request, "video_template.html", {"url":video_url})