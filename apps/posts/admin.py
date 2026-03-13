from django.contrib import admin
from .models import Post

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