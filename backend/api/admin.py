from django.contrib import admin
from .models import User, CodeNest, Version, Rating, Feedback, Favorite, Integration, Subscription

# PUBLIC_INTERFACE
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'is_staff']

# PUBLIC_INTERFACE
@admin.register(CodeNest)
class CodeNestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'language', 'framework', 'category', 'author', 'created_at', 'is_public', 'is_approved']

# PUBLIC_INTERFACE
@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'nest', 'major', 'minor', 'patch', 'uploader', 'created_at']

# PUBLIC_INTERFACE
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'nest', 'user', 'score', 'created_at']

# PUBLIC_INTERFACE
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'nest', 'created_at', 'resolved']

# PUBLIC_INTERFACE
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'nest', 'created_at']

# PUBLIC_INTERFACE
@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'nest', 'version', 'added_by', 'created_at']

# PUBLIC_INTERFACE
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'plan', 'status', 'started_at', 'ends_at']

