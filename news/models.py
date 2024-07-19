from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        rating_post = Post.objects.filter(author=self).aggregate(Sum('rating'))['rating__sum'] * 3
        rating_comment = Comment.objects.filter(user=self.user).aggregate(Sum('rating'))['rating__sum']
        rating_post_comment = (
            Comment.objects.filter(post__author__user=self.user).aggregate(Sum('rating')))['rating__sum']

        self.rating = rating_post + rating_comment + rating_post_comment
        self.save()


class Category(models.Model):
    name_category = models.CharField(max_length=255, unique=True)
    subscribe = models.ManyToManyField(User)


class Post(models.Model):

    article = 'AT'
    news = 'NW'
    categories = [(article, 'Article'),
                  (news, 'News')]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.CharField(max_length=2, choices=categories)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    text = models.TextField(max_length=255)
    category = models.ManyToManyField(Category, through='PostCategory')
    rating = models.IntegerField(default=0)

    def post_like(self):
        self.rating += 1
        self.save()

    def post_dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_comment = models.CharField(max_length=255)
    time_com = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def com_like(self):
        self.rating += 1
        self.save()

    def com_dislike(self):
        self.rating -= 1
        self.save()


class CategorySubscribe(models.Model):

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    subscriber = models.ForeignKey(User, on_delete=models.PROTECT)
