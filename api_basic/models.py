from django.db import models


# Create your models here.


class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


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
class Report(models.Model):
    student = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    fulldate = models.DateTimeField()
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

class Count(models.Model):
    student = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    fulldate = models.DateTimeField()
    countLnCh = models.FloatField()
    countSlalom = models.FloatField()
    passedLnCh = models.FloatField()
    passedSlalom = models.FloatField()
    avScoreLnCh = models.FloatField()
    avScoreSlalom = models.FloatField()
    startScoreLnCh = models.FloatField()
    startScoreSlalom = models.FloatField()
    endScoreLnCh = models.FloatField()
    endScoreSlalom = models.FloatField()
    lnChPassed = models.FloatField()
    slalomPassed = models.FloatField()

    def __str__(self):
        return self.student


class FinalExercise(models.Model):
    student = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    program = models.CharField(max_length=100)
    fulldate = models.DateTimeField()
    carId = models.IntegerField()
    stress = models.IntegerField()
    revSlalom = models.CharField(max_length=100)
    revPc = models.FloatField()
    slalom = models.FloatField()
    lnCh = models.FloatField()
    cones = models.IntegerField()
    gates = models.IntegerField()
    fTime = models.CharField(max_length=100)
    finalResult = models.FloatField()

    def __str__(self):
        return self.student







