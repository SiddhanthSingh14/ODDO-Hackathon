from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import MaintenanceTeam, UserProfile, Equipment, MaintenanceRequest
from .serializers import (
    MaintenanceTeamSerializer, UserProfileSerializer, EquipmentSerializer,
    MaintenanceRequestSerializer, NotificationSerializer
)
from .models import MaintenanceTeam, UserProfile, Equipment, MaintenanceRequest, Notification


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for Notification CRUD operations"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        """Filter notifications by current user"""
        user = self.request.user
        if user.is_authenticated:
            return self.queryset.filter(recipient=user)
        return self.queryset.none()
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})



class MaintenanceTeamViewSet(viewsets.ModelViewSet):
    """ViewSet for MaintenanceTeam CRUD operations"""
    queryset = MaintenanceTeam.objects.all()
    serializer_class = MaintenanceTeamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['team_name']
    ordering_fields = ['team_name']


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile CRUD operations"""
    queryset = UserProfile.objects.select_related('user', 'team').all()
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'team']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering_fields = ['user__username', 'role']
    
    @action(detail=False, methods=['get'])
    def technicians(self, request):
        """Get all users with technician role"""
        technicians = self.queryset.filter(role='technician')
        team_id = request.query_params.get('team_id')
        if team_id:
            technicians = technicians.filter(team_id=team_id)
        serializer = self.get_serializer(technicians, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_team(self, request):
        """Get users by team ID"""
        team_id = request.query_params.get('team_id')
        if not team_id:
            return Response({'error': 'team_id parameter is required'}, status=400)
        users = self.queryset.filter(team_id=team_id)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class EquipmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Equipment CRUD operations"""
    queryset = Equipment.objects.select_related('maintenance_team').all()
    serializer_class = EquipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['maintenance_team', 'department', 'is_active']
    search_fields = ['name', 'serial_number', 'owner_name']
    ordering_fields = ['name', 'purchase_date']
    
    @action(detail=False, methods=['get'])
    def by_team(self, request):
        """Get equipment by team ID"""
        team_id = request.query_params.get('team_id')
        if not team_id:
            return Response({'error': 'team_id parameter is required'}, status=400)
        equipment = self.queryset.filter(maintenance_team_id=team_id, is_active=True)
        serializer = self.get_serializer(equipment, many=True)
        return Response(serializer.data)


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for MaintenanceRequest CRUD operations"""
    queryset = MaintenanceRequest.objects.select_related(
        'equipment', 'team', 'technician'
    ).all()
    serializer_class = MaintenanceRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'request_type', 'team', 'technician']
    search_fields = ['subject', 'equipment__name']
    ordering_fields = ['created_at', 'due_date', 'scheduled_date']
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get maintenance requests grouped by status (for Kanban board)"""
        statuses = dict(MaintenanceRequest.STATUS_CHOICES)
        result = {}
        for status_key, status_label in statuses.items():
            requests = self.queryset.filter(status=status_key)
            serializer = self.get_serializer(requests, many=True)
            result[status_key] = {
                'label': status_label,
                'count': requests.count(),
                'items': serializer.data
            }
        return Response(result)
