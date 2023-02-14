from django.contrib import admin

from dlp.models import Pattern, Match, Message


class MessageInline(admin.TabularInline):
    model = Message
    fields = ['text', 'timestamp', 'author', 'connector', 'match']
    extra = 0


class PatternInline(admin.TabularInline):
    model = Pattern
    fields = ['fixture', 'date_created', 'created_by', 'active', 'match']
    extra = 0


class MathInline(admin.TabularInline):
    model = Match
    fields = ['message']
    extra = 0

class MatchAdmin(admin.ModelAdmin):
    model = Match
    list_display = ['pattern', 'message__text', 'message__author', 'message__timestamp']
    list_filter = ['pattern', 'message__connector']
    search_fields = ['pattern__fixture', 'message__text', 'message__author']

    def message__author(self, obj):
        return obj.message.author

    def message__timestamp(self, obj):
        return obj.message.timestamp

    def message__text(self, obj):
        return obj.message.text[:100]+'…'

class PatternAdmin(admin.ModelAdmin):
    model = Pattern
    inlines = [MathInline]
    list_display = ['active','fixture', 'date_created']
    list_filter = ['active', 'created_by']
    search_fields = ['fixture']
    list_display_links = list_display
    editable_fields = ['active']
    readonly_fields = ['date_created', 'created_by']

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'created_by', None) is None:
            obj.created_by = request.user
        obj.save()

admin.site.register(Message)
admin.site.register(Pattern, PatternAdmin)
admin.site.register(Match, MatchAdmin)
