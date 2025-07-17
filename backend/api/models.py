from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# PUBLIC_INTERFACE
class User(AbstractUser):
    """Custom user model with support for OAuth/email, mobile number, and basic profile details."""
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True, unique=True, help_text="User's mobile phone number.")
    # Email field (already in AbstractUser)
    # Username field (already in AbstractUser)
    # Password field (already in AbstractUser)


LANG_CHOICES = [
    ('python', 'Python'),
    ('js', 'JavaScript'),
    ('java', 'Java'),
    ('go', 'Go'),
    ('cpp', 'C++'),
    ('ts', 'TypeScript'),
    ('csharp', 'C#'),
    ('ruby', 'Ruby'),
    ('php', 'PHP'),
    ('other', 'Other'),
]

FRAMEWORK_CHOICES = [
    ('django', 'Django'),
    ('react', 'React'),
    ('vue', 'Vue'),
    ('flask', 'Flask'),
    ('spring', 'Spring'),
    ('express', 'Express'),
    ('angular', 'Angular'),
    ('none', 'None/Vanilla'),
    ('other', 'Other'),
]

CATEGORY_CHOICES = [
    ('auth', 'Authentication'),
    ('db', 'Database'),
    ('ui', 'UI'),
    ('api', 'API'),
    ('infra', 'Infrastructure'),
    ('test', 'Testing'),
    ('other', 'Other'),
]


# PUBLIC_INTERFACE
class CodeNest(models.Model):
    """
    Represents a contributed code module/template.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(max_length=20, choices=LANG_CHOICES)
    framework = models.CharField(max_length=20, choices=FRAMEWORK_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='code_nests')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    tags = models.CharField(max_length=200, blank=True)
    integration_instructions = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    # current_version points to the most recent Version
    current_version = models.ForeignKey('Version', null=True, blank=True, related_name="current_for", on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

# PUBLIC_INTERFACE
class Version(models.Model):
    """
    Version of a CodeNest, with associated code.
    """
    nest = models.ForeignKey(CodeNest, on_delete=models.CASCADE, related_name='versions')
    major = models.PositiveIntegerField(default=1)
    minor = models.PositiveIntegerField(default=0)
    patch = models.PositiveIntegerField(default=0)
    changelog = models.TextField(blank=True)
    code = models.TextField()  # Could be a link (URLField), file, or text
    created_at = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nest.name} v{self.major}.{self.minor}.{self.patch}"

    class Meta:
        unique_together = ('nest', 'major', 'minor', 'patch')
        ordering = ["-created_at"]

# PUBLIC_INTERFACE
class Rating(models.Model):
    """
    Star rating (1-5) with optional review.
    """
    nest = models.ForeignKey(CodeNest, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('nest', 'user')

# PUBLIC_INTERFACE
class Feedback(models.Model):
    """
    User feedback (bugs, requests) per CodeNest or overall.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    nest = models.ForeignKey(CodeNest, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)

# PUBLIC_INTERFACE
class Favorite(models.Model):
    """
    User-favorited/bookmarked CodeNests.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    nest = models.ForeignKey(CodeNest, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'nest')

# PUBLIC_INTERFACE
class Integration(models.Model):
    """
    Example integrations or code snippets provided for each CodeNest/version.
    """
    nest = models.ForeignKey(CodeNest, on_delete=models.CASCADE, related_name='integrations')
    version = models.ForeignKey(Version, on_delete=models.CASCADE, related_name='integrations')
    content = models.TextField()
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

# PUBLIC_INTERFACE
class Subscription(models.Model):
    """
    Simple billing/subscription stub (expand for Stripe, etc).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=[('trial', 'Trial'), ('active', 'Active'), ('canceled', 'Canceled')], default='trial')
    started_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    plan = models.CharField(max_length=30, default='free')

    class Meta:
        unique_together = ('user', 'plan')
