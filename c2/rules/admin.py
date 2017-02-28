from django.contrib import admin

from c2.rules.models import Rule, RuleConfiguration

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('slug', '__unicode__', 'description')
    search_fields = ('name', 'slug', )
    prepopulated_fields = { 'slug': ('name', ) }

@admin.register(RuleConfiguration)
class RuleConfigurationAdmin(admin.ModelAdmin):
    list_display = ('rule', 'team', 'enabled', )
    list_filter = ('rule', 'enabled', )