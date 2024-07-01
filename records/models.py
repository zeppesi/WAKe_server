from django.db import models



class Content(models.Model):
    text = models.TextField(blank=False, null=False)
    is_active = models.BooleanField(default=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Record(models.Model):
    profile = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)

    text = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
