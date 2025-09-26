from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class ChatSession(models.Model):
    """Model for storing AI chat sessions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    context_metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        db_table = 'ai_chat_sessions'
        
    def __str__(self):
        return f"Chat Session {self.session_name or self.id}"


class ChatMessage(models.Model):
    """Model for storing individual chat messages."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    token_count = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        db_table = 'ai_chat_messages'
        
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class VectorEmbedding(models.Model):
    """Model for storing vector embeddings for RAG."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField()
    content_hash = models.CharField(max_length=64, db_index=True)
    embedding_vector = models.JSONField()  # Store as JSON array
    embedding_model = models.CharField(max_length=100)
    source_type = models.CharField(max_length=50)  # document, message, etc.
    source_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ['content_hash', 'embedding_model']
        db_table = 'ai_vector_embeddings'
        indexes = [
            models.Index(fields=['source_type', 'source_id']),
            models.Index(fields=['embedding_model']),
        ]
        
    def __str__(self):
        return f"Embedding: {self.content[:30]}... ({self.embedding_model})"


class ActionSuggestion(models.Model):
    """Model for storing AI-generated action suggestions."""
    SUGGESTION_TYPES = [
        ('workflow', 'Workflow Suggestion'),
        ('optimization', 'Optimization'),
        ('alert', 'Alert'),
        ('recommendation', 'Recommendation'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confidence_score = models.FloatField(null=True, blank=True)  # AI confidence 0-1
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    context_data = models.JSONField(default=dict, blank=True)
    action_payload = models.JSONField(default=dict, blank=True)  # Data needed to execute action
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'ai_action_suggestions'
        indexes = [
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['user', 'status']),
        ]
        
    def __str__(self):
        return f"{self.title} ({self.priority})"
