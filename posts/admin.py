from django.contrib import admin
from .models import Post, Comment, Category, cat_post_linker

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(cat_post_linker)