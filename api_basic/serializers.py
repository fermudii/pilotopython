from rest_framework import serializers
from .models import Article, Piloto

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'author']
        #fields = '__all__'

class PilotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Piloto
        fields = '__all__'
