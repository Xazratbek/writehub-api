from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class PostStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"

class Tag(models.Model):
    name = models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=60,unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "tags"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    tags = models.ManyToManyField("posts.Tag",through="posts.PostTag",related_name="posts",blank=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="posts.PostLike",
        related_name="liked_posts",
        blank=True,
    )
    bookmarked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="posts.Bookmark",
        related_name="bookmarked_posts",
        blank=True,
    )
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to="posts/covers/", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT,
    )
    reading_time = models.PositiveIntegerField(default=1)
    views_count = models.PositiveBigIntegerField(default=0)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "posts"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["author", "slug"],
                name="unique_author_slug",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["author", "status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.content:
            word_count = len(self.content.split())
            calculated_reading_time = max(1, word_count // 200)
            self.reading_time = calculated_reading_time

        if self.status == PostStatus.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        if self.status != PostStatus.PUBLISHED:
            self.published_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PostTag(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="post_tags")
    tag = models.ForeignKey("posts.Tag",on_delete=models.CASCADE,related_name="tag_posts")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "post_tags"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["post","tag"],
                name="unique_post_tag",
            )
        ]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["tag"]),
        ]

        def __str__(self):
            return f"{self.post_id} -> {self.tag.name}"

class Comment(models.Model):
    post = models.ForeignKey("posts.Post",on_delete=models.CASCADE,related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="comments")
    parent = models.ForeignKey("self",on_delete=models.CASCADE,related_name="replies",blank=True,null=True)
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post","created_at"]),
            models.Index(fields=["author"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["deleted_at"]),
        ]

    def clean(self):
        if self.parent and self.parent.post_id != self.post_id:
            raise ValueError("Parent id aynan shu postga tegishli bo'lishi kerak")

    def save(self,*args, **kwargs):
        if self.pk:
            original = Comment.objects.filter(pk=self.pk).only("content").first()
            if original and original.content != self.content:
                self.is_edited = True

        self.full_clean()
        super().save(*args,**kwargs)

    def __str__(self):
        return f"Comment<{self.id}> by {self.author.email}"

class PostLike(models.Model):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="post_likes"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="user_post_likes")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "post_likes"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["post","user"], name="unique_post_like"
            ),
        ]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Like<post={self.post_id}, user={self.user_id}>"

class Bookmark(models.Model):
    post = models.ForeignKey("posts.Post",on_delete=models.CASCADE,related_name="post_bookmarks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name="user_bookmarks")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "bookmarks"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["post","user"], name="unique_post_bookmark"
            ),
        ]
        indexes = [
            models.Index(fields=["post"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Bookmark<post={self.post_id}, user={self.user_id}>"


class PostView(models.Model):
    post = models.ForeignKey("posts.Post",on_delete=models.CASCADE,related_name="post_views")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="viewed_posts_log",blank=True,null=True
    )
    ip_address = models.GenericIPAddressField(blank=True,null=True)
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "post_views"
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["post","viewed_at"]),
            models.Index(fields=["user"]),
            models.Index(fields=["ip_address"]),
            models.Index(fields=["viewed_at"]),
        ]

    def __str__(self):
        return f"PostView<post={self.post_id}, user={self.user_id}, viewed_at={self.viewed_at}>"