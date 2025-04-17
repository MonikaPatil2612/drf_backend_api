from rest_framework import serializers
from .models import DataFile, Visualization

class DataFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFile
        fields = ['id', 'name', 'file', 'uploaded_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class VisualizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visualization
        fields = ['id', 'title', 'description', 'type', 'config', 'data_file', 'created_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
