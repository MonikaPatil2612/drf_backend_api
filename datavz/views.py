from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import json
from .models import DataFile, Visualization
from .serializers import DataFileSerializer, VisualizationSerializer

class DataFileViewSet(viewsets.ModelViewSet):
    queryset = DataFile.objects.all()
    serializer_class = DataFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DataFile.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def preview_data(self, request, pk=None):
        """Preview the data from an Excel file"""
        data_file = self.get_object()
        
        try:
            df = pd.read_excel(data_file.file.path)
            preview = df.head(10).to_dict(orient='records')
            columns = df.columns.tolist()
            
            return Response({
                'preview': preview,
                'columns': columns,
                'total_rows': len(df)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VisualizationViewSet(viewsets.ModelViewSet):
    queryset = Visualization.objects.all()
    serializer_class = VisualizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Visualization.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def generate(self, request, pk=None):
        visualization = self.get_object()
        data_file = visualization.data_file
        
        try:
            df = pd.read_excel(data_file.file.path)
            config = visualization.config
            chart_type = visualization.type
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'bar':
                x_column = config.get('x_column')
                y_column = config.get('y_column')
                df.plot(kind='bar', x=x_column, y=y_column)
                plt.title(visualization.title)
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                
            elif chart_type == 'line':
                x_column = config.get('x_column')
                y_columns = config.get('y_columns', [])
                df.plot(kind='line', x=x_column, y=y_columns)
                plt.title(visualization.title)
                plt.xlabel(x_column)
                plt.ylabel('Values')
                
            elif chart_type == 'pie':
                values = config.get('values')
                labels = config.get('labels')
                df[values].plot(kind='pie', labels=df[labels])
                plt.title(visualization.title)
                
            elif chart_type == 'scatter':
                x_column = config.get('x_column')
                y_column = config.get('y_column')
                df.plot(kind='scatter', x=x_column, y=y_column)
                plt.title(visualization.title)
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                
            else:
                return Response({'error': 'Unsupported chart type'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return Response({
                'image': image_base64,
                'title': visualization.title
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the visualization as a PNG file"""
        visualization = self.get_object()
        
        try:
            data_file = visualization.data_file
            df = pd.read_excel(data_file.file.path)
            config = visualization.config
            chart_type = visualization.type
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'bar':
                x_column = config.get('x_column')
                y_column = config.get('y_column')
                df.plot(kind='bar', x=x_column, y=y_column)
                plt.title(visualization.title)
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                
            elif chart_type == 'line':
                x_column = config.get('x_column')
                y_columns = config.get('y_columns', [])
                df.plot(kind='line', x=x_column, y=y_columns)
                plt.title(visualization.title)
                plt.xlabel(x_column)
                plt.ylabel('Values')
                
            elif chart_type == 'pie':
                values = config.get('values')
                labels = config.get('labels')
                df[values].plot(kind='pie', labels=df[labels])
                plt.title(visualization.title)
                
            elif chart_type == 'scatter':
                x_column = config.get('x_column')
                y_column = config.get('y_column')
                df.plot(kind='scatter', x=x_column, y=y_column)
                plt.title(visualization.title)
                plt.xlabel(x_column)
                plt.ylabel(y_column)
                
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            
            response = HttpResponse(buffer.getvalue(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{visualization.title}.png"'
            
            return response
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

