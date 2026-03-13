from django.conf import settings
from django.db import models
from django.utils import timezone


class NotificationType(models.TextChoices):
    FOLLOW = "follow", "Follow"
    POST_LIKE = "post_like", "Post like"
    COMMENT_REPLY = "comment_reply", "Comment reply"
    COMMENT_ON_POST = "comment_on_post", "Comment on post"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
    )
    type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    comment = models.ForeignKey(
        "posts.Comment",
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "created_at"]),
            models.Index(fields=["type"]),
            models.Index(fields=["created_at"]),
        ]

    def clean(self):
        if self.recipient_id == self.actor_id:
            raise ValueError("Actor and recipient cannot be the same user.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification<{self.type}> to {self.recipient_id} from {self.actor_id}"