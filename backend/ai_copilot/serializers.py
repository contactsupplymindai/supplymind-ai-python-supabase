from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage, VectorEmbedding, ActionSuggestion


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'timestamp', 'token_count', 'metadata']
        read_only_fields = ['id', 'timestamp', 'token_count']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'session_name', 'created_at', 'updated_at', 'is_active', 
                  'context_metadata', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for incoming chat requests."""
    message = serializers.CharField(max_length=10000)
    session_id = serializers.UUIDField(required=False)
    stream = serializers.BooleanField(default=False)
    model = serializers.CharField(default='gpt-3.5-turbo', max_length=50)
    temperature = serializers.FloatField(default=0.7, min_value=0.0, max_value=2.0)
    max_tokens = serializers.IntegerField(default=1000, min_value=1, max_value=4000)
    context = serializers.JSONField(default=dict, required=False)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses."""
    response = serializers.CharField()
    session_id = serializers.UUIDField()
    message_id = serializers.UUIDField()
    token_usage = serializers.JSONField(default=dict)
    model = serializers.CharField()
    processing_time = serializers.FloatField()


class EmbedRequestSerializer(serializers.Serializer):
    """Serializer for embedding generation requests."""
    text = serializers.CharField(max_length=50000)
    model = serializers.CharField(default='text-embedding-ada-002', max_length=50)
    source_type = serializers.CharField(default='document', max_length=50)
    source_id = serializers.CharField(required=False, max_length=255, allow_blank=True)
    metadata = serializers.JSONField(default=dict, required=False)


class EmbedResponseSerializer(serializers.Serializer):
    """Serializer for embedding responses."""
    embedding_id = serializers.UUIDField()
    vector = serializers.ListField(child=serializers.FloatField())
    model = serializers.CharField()
    token_count = serializers.IntegerField()
    processing_time = serializers.FloatField()


class VectorEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer for vector embeddings."""
    
    class Meta:
        model = VectorEmbedding
        fields = ['id', 'content', 'content_hash', 'embedding_vector', 
                  'embedding_model', 'source_type', 'source_id', 
                  'created_at', 'metadata']
        read_only_fields = ['id', 'content_hash', 'created_at']


class SemanticSearchRequestSerializer(serializers.Serializer):
    """Serializer for semantic search requests."""
    query = serializers.CharField(max_length=1000)
    top_k = serializers.IntegerField(default=5, min_value=1, max_value=50)
    threshold = serializers.FloatField(default=0.7, min_value=0.0, max_value=1.0)
    source_types = serializers.ListField(
        child=serializers.CharField(max_length=50), 
        required=False
    )
    filters = serializers.JSONField(default=dict, required=False)
    include_embeddings = serializers.BooleanField(default=False)


class SemanticSearchResultSerializer(serializers.Serializer):
    """Serializer for semantic search results."""
    content = serializers.CharField()
    similarity_score = serializers.FloatField()
    source_type = serializers.CharField()
    source_id = serializers.CharField(allow_blank=True)
    metadata = serializers.JSONField()
    embedding_id = serializers.UUIDField()
    embedding_vector = serializers.ListField(
        child=serializers.FloatField(), 
        required=False
    )


class SemanticSearchResponseSerializer(serializers.Serializer):
    """Serializer for semantic search responses."""
    results = SemanticSearchResultSerializer(many=True)
    query_embedding = serializers.ListField(
        child=serializers.FloatField(), 
        required=False
    )
    total_results = serializers.IntegerField()
    processing_time = serializers.FloatField()


class ActionSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for action suggestions."""
    
    class Meta:
        model = ActionSuggestion
        fields = ['id', 'suggestion_type', 'title', 'description', 'priority', 
                  'status', 'confidence_score', 'created_at', 'updated_at', 
                  'context_data', 'action_payload']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SuggestionRequestSerializer(serializers.Serializer):
    """Serializer for action suggestion requests."""
    context = serializers.JSONField()
    suggestion_types = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False
    )
    max_suggestions = serializers.IntegerField(default=5, min_value=1, max_value=20)
    min_confidence = serializers.FloatField(default=0.5, min_value=0.0, max_value=1.0)
    user_preferences = serializers.JSONField(default=dict, required=False)


class SuggestionResponseSerializer(serializers.Serializer):
    """Serializer for suggestion responses."""
    suggestions = ActionSuggestionSerializer(many=True)
    total_suggestions = serializers.IntegerField()
    processing_time = serializers.FloatField()
    context_analysis = serializers.JSONField(default=dict)


class SuggestionStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating suggestion status."""
    status = serializers.ChoiceField(choices=ActionSuggestion.STATUS_CHOICES)
    feedback = serializers.CharField(required=False, max_length=1000)
    implementation_notes = serializers.CharField(required=False, max_length=2000)
