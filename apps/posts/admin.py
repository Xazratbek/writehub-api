from django.contrib import admin
from .models import *


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title","author","status","reading_time","views_count","published_at","created_at"
    ]
    list_filter = ["status","created_at","published_at"]
    search_fields = ["title","slug","author__email","author__username"]
    readonly_fields = ["reading_time","views_count","published_at","created_at","updated_at"]
    prepopulated_fields = {"slug": ('title',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["id","name","slug","created_at"]
    search_fields = ["name","slug"]
    readonly_fields = ["created_at"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ["id","post","tag","created_at"]
    search_fields = ["post__title","tag__name"]
    readonly_fields = ["created_at"]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id","post","author","parent","is_edited","deleted_at","created_at"]
    list_filter = ["is_edited","deleted_at","created_at"]
    search_fields = ["content","author__email","author__username","post__title"]
    readonly_fields = ["is_edited","created_at","updated_at"]


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["id","post","user","created_at"]
    search_fields = ["post__title","user__email","user__username"]
    readonly_fields = ["created_at"]

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["id","post","user","created_at"]
    search_fields = ["post__title","user__email","user__username"]
    readonly_fields = ["created_at"]

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ["id","post","user","ip_address","viewed_at"]
    search_fields = ["post__title","user__email","user__username","ip_address"]
    readonly_fields = ["viewed_at"]