from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")

        if not username:
            raise ValueError("Username is required.")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    following = models.ManyToManyField(
        "self",
        through="users.Follow",
        symmetrical=False,
        related_name="followers",
        blank=True
    )
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField("users.User",on_delete=models.CASCADE,related_name="profile")
    full_name = models.CharField(max_length=255,blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/",blank=True,null=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=255,blank=True)
    birth_date = models.DateField(blank=True,null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profile<{self.user.email}>"


class Follow(models.Model):
    follower = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,related_name="following_relationships"
    )
    following = models.ForeignKey("users.User",on_delete=models.CASCADE,related_name="follower_relationships")
    created_at = models.DateTimeField(default=timezone.now())

    class Meta:
        db_table = "follows"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["follower","following"],name="unique_follow_relationship"
            )
        ]
        indexes = (
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
            models.Index(fields=["created_at"]),
        )

    def clean(self):
        if self.follower_id == self.following_id:
            raise ValueError("Foydalanuvchi o'ziga o'zi obuna bo'la olmaydi")

    def save(self,*args, **kwargs):
        self.full_clean()
        super().save(*args,**kwargs)

    def __str__(self):
        return f"Follow<follower={self.follower_id}, following={self.following_id}>"