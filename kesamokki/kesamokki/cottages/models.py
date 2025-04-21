from django.db import models
from django.utils.text import slugify

class Cottage(models.Model):
    name         = models.CharField(max_length=80)
    slug         = models.SlugField(unique=True, blank=True)
    description  = models.TextField()
    location     = models.CharField(max_length=120)  # e.g. "Rovaniemi, Lapland"
    beds         = models.PositiveSmallIntegerField()
    base_price   = models.DecimalField(max_digits=8, decimal_places=2)  # €/night
    cleaning_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    active       = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CottageImage(models.Model):
    cottage  = models.ForeignKey(Cottage, related_name="images", on_delete=models.CASCADE)
    image    = models.ImageField(upload_to="cottages/")
    alt_text = models.CharField(max_length=120, blank=True)
    order    = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("cottage", "order")

    def __str__(self):
        return f"{self.cottage.name} – #{self.order}"