from django.contrib import admin

from .models import Birthday, Tag

admin.site.empty_value_display = 'Не задано'


@admin.register(Birthday)
class BirthdayAdmin(admin.ModelAdmin):
    list_display = (
        'birthday',
    )

    def __str__(self):
        return self.title


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'tag',
    )

    def __str__(self):
        return self.title