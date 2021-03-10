from rest_framework import serializers
from .models import Article, Piloto, Report, Count, FinalExercise

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'author']
        #fields = '__all__'

class PilotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piloto
        fields = '__all__'
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class CountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Count
        fields = '__all__'

class FinalExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalExercise
        fields = '__all__'