from django.db import models


# Create your models here.


#class Article(models.Model):
 #   title = models.CharField(max_length=100)
  #  author = models.CharField(max_length=100)
   # email = models.CharField(max_length=100)
    #date = models.DateTimeField(auto_now_add=True)

    #def __str__(self):
     #   return self.title


#class Piloto(models.Model):
#    student = models.CharField(max_length=100)
#    company = models.CharField(max_length=100)
#    program = models.CharField(max_length=100)
#    fulldate = models.CharField(max_length=100)
#    vehicle = models.CharField(max_length=100, default="empty")
#    snor = models.CharField(max_length=100, default="empty")
#    spoce = models.CharField(max_length=100, default="empty")
#    saoep = models.CharField(max_length=100, default="empty")
#    saovc = models.CharField(max_length=100, default="empty")
#    sfpl = models.CharField(max_length=100, default="empty")
#    lnor = models.CharField(max_length=100, default="empty")
#    lpoce = models.CharField(max_length=100, default="empty")
#    laoep = models.CharField(max_length=100, default="empty")
#    laovc = models.CharField(max_length=100, default="empty")
#    lfpl = models.CharField(max_length=100, default="empty")

 #   def __str__(self):
 #       return self.student
#class Report(models.Model):
#    student = models.CharField(max_length=100)
#    company = models.CharField(max_length=100)
#    program = models.CharField(max_length=100)
#    fulldate = models.DateTimeField()
#    vehicle = models.CharField(max_length=100, default="empty")
#    snor = models.CharField(max_length=100, default="empty")
#    spoce = models.CharField(max_length=100, default="empty")
#    saoep = models.CharField(max_length=100, default="empty")
#    saovc = models.CharField(max_length=100, default="empty")
#    sfpl = models.CharField(max_length=100, default="empty")
#    lnor = models.CharField(max_length=100, default="empty")
#    lpoce = models.CharField(max_length=100, default="empty")
#    laoep = models.CharField(max_length=100, default="empty")
#    laovc = models.CharField(max_length=100, default="empty")
#    lfpl = models.CharField(max_length=100, default="empty")

 #   def __str__(self):
 #       return self.student

#class Count(models.Model):
#    student = models.CharField(max_length=100)
#    company = models.CharField(max_length=100)
#    program = models.CharField(max_length=100)
#    fulldate = models.DateTimeField()
#    countLnCh = models.FloatField()
#    countSlalom = models.FloatField()
#    passedLnCh = models.FloatField()
#    passedSlalom = models.FloatField()
#    avScoreLnCh = models.FloatField()
#    avScoreSlalom = models.FloatField()
#    startScoreLnCh = models.FloatField()
#    startScoreSlalom = models.FloatField()
#    endScoreLnCh = models.FloatField()
#    endScoreSlalom = models.FloatField()
#    lnChPassed = models.FloatField()
#    slalomPassed = models.FloatField()

 #   def __str__(self):
 #       return self.student


#class FinalExercise(models.Model):
#    student = models.CharField(max_length=100)
#    company = models.CharField(max_length=100)
#    program = models.CharField(max_length=100)
#    fulldate = models.DateTimeField()
#    carId = models.IntegerField()
#    stress = models.IntegerField()
#    revSlalom = models.CharField(max_length=100)
#    revPc = models.FloatField()
#    slalom = models.FloatField()
#    lnCh = models.FloatField()
#    cones = models.IntegerField()
#    gates = models.IntegerField()
#    fTime = models.CharField(max_length=100)
#    finalResult = models.FloatField()

 #   def __str__(self):
 #       return self.student

#class SlalomAvg(models.Model):
#    student = models.CharField(max_length=100)
#    company = models.CharField(max_length=100)
#    program = models.CharField(max_length=100)
#    fulldate = models.DateTimeField()
#    vehiclePcAvgLnCh = models.FloatField()
#    vehiclePcAvgSlalom = models.FloatField()

 #   def __str__(self):
 #       return self.student

#class Comments(models.Model):
#    student = models.CharField(max_length=100)
#    company = models.CharField(max_length=100)
#    program = models.CharField(max_length=100)
#    fulldate = models.DateTimeField()
#    comment = models.CharField(max_length=10000)

 #   def __str__(self):
 #       return self.student

#class Course(models.Model):
#    student = models.CharField(max_length=100)
#    company = models.CharField(max_length=100)
#    program = models.CharField(max_length=100)
#    fulldate = models.DateTimeField()
#    exercise = models.CharField(max_length=100)
#    pcExercise = models.FloatField()
#    pcVehicle = models.FloatField()

class Courses(models.Model):
    idCompany = models.IntegerField()
    idVenue = models.IntegerField()
    idProgram = models.IntegerField()
    available = models.IntegerField()
    eventDate = models.DateTimeField()
    idealTime = models.FloatField()
    conePenalty = models.IntegerField()
    gatePenalty = models.IntegerField()
    excelLoaded = models.BooleanField(blank=True, null=True)

class Vehicles(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    make = models.FloatField()
    model = models.CharField(max_length=100)
    latAcc = models.FloatField()
    active = models.BooleanField()

class Exercises(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField()

class CoursesStudents(models.Model):
    idCourse = models.IntegerField()
    idStudent = models.IntegerField()

class VehiclesSelected(models.Model):
    idCourse = models.IntegerField()
    idVehicle = models.IntegerField()
    csvLoadedDataFinalExercise = models.BooleanField(blank=True, null=True)
    csvLoadedDataExercise = models.BooleanField(blank=True, null=True)

class ExercisesSelected(models.Model):
    idCourse = models.IntegerField()
    idExercise = models.IntegerField()
    chord = models.IntegerField()
    mo = models.FloatField()

class FinalExercisesSelected(models.Model):
    idCourse = models.IntegerField()
    idExercise = models.IntegerField()
    chord = models.IntegerField()
    mo = models.FloatField()

class Comments(models.Model):
    idStudent = models.IntegerField()
    idCourse = models.IntegerField()
    comment = models.CharField(max_length=10000)

class Venues(models.Model):
    idCountry = models.IntegerField()
    state = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    active = models.BooleanField(max_length=100)

class Countries(models.Model):
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=100)
    active = models.BooleanField()

class Programs(models.Model):
    name = models.CharField(max_length=100)
    durationDays = models.IntegerField()
    active = models.BooleanField()

class Users(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    active = models.BooleanField()
    emailVerified = models.BooleanField()
    tokenExpired = models.BooleanField()
    idCountry = models.IntegerField()

class Companies(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    primaryContact = models.CharField(max_length=100)
    idUser = models.IntegerField()
    active = models.BooleanField()

class Students(models.Model):
    idCompany = models.IntegerField()
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    birthday = models.DateField()
    idUser = models.IntegerField()

class ProfilesUsers(models.Model):
    idUser = models.IntegerField()
    idProfile = models.IntegerField()

class Profiles(models.Model):
    profile = models.CharField(max_length=100)

class DataExercises(models.Model):
    idCourse = models.IntegerField()
    idStudent = models.IntegerField()
    idExerciseSelected = models.IntegerField()
    idVehicleSelected = models.IntegerField()
    speedReq = models.IntegerField()
    v1 = models.FloatField()
    v2 = models.FloatField()
    v3 = models.FloatField()
    penalties = models.IntegerField()

class DataFinalExercise(models.Model):
    idCourse = models.IntegerField()
    idStudent = models.IntegerField()
    idVehicleSelected = models.IntegerField()
    stressLevel = models.IntegerField()
    revSlalom = models.FloatField(blank=True, null=True)
    slalom = models.FloatField(blank=True, null=True)
    laneChange = models.FloatField(blank=True, null=True)
    cones = models.IntegerField()
    gates = models.IntegerField()
    time = models.FloatField()

class DataFinalExercisePc(models.Model):
    idCourse = models.IntegerField()
    idStudent = models.IntegerField()
    rev = models.FloatField()
    slalom = models.IntegerField()
    laneChange = models.IntegerField()
    cones = models.IntegerField()
    gates = models.IntegerField()
    finalTime = models.FloatField()
    finalResult = models.FloatField()

class PPR(models.Model):
    idCourse = models.IntegerField()
    idStudent = models.IntegerField()
    idCompany = models.IntegerField()
    idCountry = models.IntegerField()
    PPR = models.IntegerField()
    runs = models.IntegerField()
    eventDate = models.DateTimeField()

class StudentRecords(models.Model):
    idStudent = models.IntegerField()
    idCompany = models.IntegerField()
    registerDate = models.DateTimeField()

















