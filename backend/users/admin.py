from django.contrib import admin

from users.models import CustomUser, Subscribe


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'username'
    )
    list_filter = ('email', 'first_name')
    search_fields = ('username', 'email')


@admin.register(Subscribe)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'user__email')
