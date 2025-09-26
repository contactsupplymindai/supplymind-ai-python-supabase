from django.urls import path
from . import views

app_name = 'ai_copilot'

urlpatterns = [
    # Chat Copilot endpoint
    path('api/copilot/chat/', views.ChatCopilot, name='chat'),
    
    # Vector RAG: embedding generation endpoint
    path('api/copilot/embed/', views.Embed, name='embed'),
    
    # Semantic search endpoint
    path('api/copilot/search/', views.SemanticSearch, name='search'),
    
    # Action suggestions endpoint
    path('api/copilot/suggest/', views.Suggest, name='suggest'),
]
