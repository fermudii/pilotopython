from rest_framework import serializers
from .models import Courses, CoursesStudents, Exercises, ExercisesSelected, VehiclesSelected, Vehicles, Comments, Countries, Venues, Programs, DataExercises, DataFinalExercise, DataFinalExercisePc, PPR

#class ArticleSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Article
#        fields = ['id', 'title', 'author']
        #fields = '__all__'

#class PilotoSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Piloto
#        fields = '__all__'
#class ReportSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Report
#        fields = '__all__'

#class CountSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Count
#        fields = '__all__'

#class FinalExerciseSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = FinalExercise
#        fields = '__all__'

#class SlalomAvgSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = SlalomAvg
#        fields = '__all__'

#class CommentsSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Comments
#        fields = '__all__'

#class CourseSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Course
#        fields = '__all__'

class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'

class VehiclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicles
        fields = '__all__'

class ExercisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercises
        fields = '__all__'

class VehiclesSelectedSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiclesSelected
        fields = '__all__'

class ExercisesSelectedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExercisesSelected
        fields = '__all__'

class CoursesStudentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursesStudents
        fields = '__all__'

class CommentssSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'

class VenuesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venues
        fields = '__all__'

class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Countries
        fields = '__all__'

class ProgramsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Programs
        fields = '__all__'

class DataExercisesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataExercises
        fields = '__all__'

class DataFinalExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFinalExercise
        fields = '__all__'

class DataFinalExercisePcSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFinalExercisePc
        fields = '__all__'

class PPRSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPR
        fields = '__all__'



