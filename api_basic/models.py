from django.db import models


# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

1
class Piloto(models.Model):
    student = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    fulldate = models.CharField(max_length=100)
    vehicle = models.CharField(max_length=100, default="empty")
    snor = models.CharField(max_length=100, default="empty")
    spoce = models.CharField(max_length=100, default="empty")
    saoep = models.CharField(max_length=100, default="empty")
    saovc = models.CharField(max_length=100, default="empty")
    sfpl = models.CharField(max_length=100, default="empty")
    lnor = models.CharField(max_length=100, default="empty")
    lpoce = models.CharField(max_length=100, default="empty")
    laoep = models.CharField(max_length=100, default="empty")
    laovc = models.CharField(max_length=100, default="empty")
    lfpl = models.CharField(max_length=100, default="empty")

    def __str__(self):
        return self.student
