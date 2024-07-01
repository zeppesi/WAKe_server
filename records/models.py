from django.db import models


def product_image_path(instance):
    return 'zeppesi/WAKe/contents/{}'.format(instance.id)


class Content(models.Model):
    text = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to=product_image_path)
    is_active = models.BooleanField(default=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Record(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
