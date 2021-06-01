from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext as _
from derbot.names.models import DerbyName


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
class NameAdmin(admin.ModelAdmin):
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
    actions = ["mark_cleared"]

    @admin.action(description="Mark selected names as cleared for tooting")
    def mark_cleared(self, request, queryset):
        queryset.update(cleared=True)
