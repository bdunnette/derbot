from derbot.names.models import DerbyName
from derbot.names.tasks import generate_jersey, toot_name, generate_tank
from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext as _
from import_export.admin import ImportExportMixin


class FavouritesFilter(admin.SimpleListFilter):
    title = _("Favourited")
    parameter_name = "faved"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(favourites_count__gt=0)
        if self.value() == "no":
            return queryset.filter(favourites_count=0)


class TootedFilter(admin.SimpleListFilter):
    title = _("Tooted")
    parameter_name = "tooted"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(~Q(tooted=None))
        if self.value() == "no":
            return queryset.filter(Q(tooted=None))


@admin.register(DerbyName)
class NameAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "generated",
        "temperature",
        "cleared",
        "registered",
        "favourites_count",
        "reblogs_count",
    )
    list_filter = ["registered", "cleared", FavouritesFilter, TootedFilter]
    actions = ["mark_cleared", "generate_jerseys", "generate_tanks", "toot_names"]

    @admin.action(description="Mark selected names as cleared for tooting")
    def mark_cleared(self, request, queryset):
        queryset.update(cleared=True)

    @admin.action(description="Generate jersey(s) for selected name(s)")
    def generate_jerseys(self, request, queryset):
        for name in queryset:
            generate_jersey(name_id=name.id)

    @admin.action(description="Generate tank top(s) for selected name(s)")
    def generate_tanks(self, request, queryset):
        for name in queryset:
            generate_tank(name_id=name.id)

    @admin.action(description="Toot selected name(s)")
    def toot_names(self, request, queryset):
        for name in queryset:
            toot_name(name_id=name.id)
