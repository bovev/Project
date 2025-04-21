from django.contrib import admin
from .models import Cottage, CottageImage

class CottageImageInline(admin.TabularInline):
    model = CottageImage
    extra = 1
    fields = ("image", "alt_text", "order")
    ordering = ("order",)

@admin.register(Cottage)
class CottageAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "beds", "base_price", "active")
    list_filter  = ("active", "location")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CottageImageInline]