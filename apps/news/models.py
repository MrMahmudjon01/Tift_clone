from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class NewsContent(models.Model):
    title = models.CharField(max_length=255)
    body = RichTextField()
    slug = models.SlugField(unique=True)

    is_published = models.BooleanField(default=False)  # Corrected field name
    publish_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # slugify kirill/o'zbek harflarini tashlab yuborishi mumkin — bo'sh slug bo'lmasin
            original_slug = slugify(self.title, allow_unicode=True) or "yangilik"
            slug, counter = original_slug, 1
            while NewsContent.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            self.slug=slug
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
