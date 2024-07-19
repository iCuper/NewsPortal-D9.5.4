from django.shortcuts import render
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Category, User, CategorySubscribe
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PostCategory
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

# Create your views here.


class PostsList(ListView):

    model = Post
    ordering = "-created_at"

    template_name = "news.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)

        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):

    model = Post
    template_name = "new.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["time_now"] = datetime.utcnow()

        return context


class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):

    form_class = PostForm
    model = Post
    template_name = 'create_news.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('news.add_post')


class PostSearch(ListView):

        model = Post
        ordering = '-created_at'
        template_name = 'news_search.html'
        context_object_name = 'posts_search'
        paginate_by = 10

        def get_queryset(self):
            queryset = super().get_queryset()
            self.filterset = PostFilter(self.request.GET, queryset=queryset)

            return self.filterset.qs

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['filterset'] = self.filterset
            return context


class PostEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):

    form_class = PostForm
    model = Post
    template_name = 'create_news.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('news.change_post')


class PostDelete(PermissionRequiredMixin, DeleteView):

    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('news.delete_post')


class CategoriesView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'categories.html', {'categories': Category.objects.all()})


class CategoryDetail(LoginRequiredMixin, DetailView):

    model = Category
    template_name = 'category.html'
    context_object_name = 'category'


def subscribe_to_category(request, pk):

    current_user = request.user
    CategorySubscribe.objects.create(category=Category.objects.get(pk=pk),
                                     subscriber=User.objects.get(pk=current_user.id))

    return render(request, 'subscribed.html')


def notify_new_post_in_category(instance, **kwargs):

    category_id = instance.post_category.id

    subscribed_users = []
    subscribed_users_1 = CategorySubscribe.objects.filter(category_id=int(category_id))

    for user in subscribed_users_1:
        subscribed_users.append(User.objects.get(id=user.subscriber_id).email)

    print(subscribed_users)

    send_mail(
        subject=f'Новый пост в категории {Category.objects.get(id=category_id)}',
        html_message=render_to_string('news.html',
                                      context={'post': instance,
                                               'category': Category.objects.get(id=category_id).category_name,
                                                 'link': f'http://127.0.0.1:8000/{instance.id}'}),
        message='',
        from_email='user123user@yandex.ru',
        recipient_list=subscribed_users
    )

    post_save.connect(notify_new_post_in_category, sender=Post)

