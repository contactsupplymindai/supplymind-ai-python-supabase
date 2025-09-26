import time
from typing import List, Dict, Any

from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import ChatSession, ChatMessage, VectorEmbedding, ActionSuggestion
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    EmbedRequestSerializer,
    EmbedResponseSerializer,
    SemanticSearchRequestSerializer,
    SemanticSearchResponseSerializer,
    SemanticSearchResultSerializer,
    SuggestionRequestSerializer,
    SuggestionResponseSerializer,
    ActionSuggestionSerializer,
)


# ---- Stub AI providers (OpenAI/HuggingFace) ----
class LLMProvider:
    """Stub for LLM chat completion provider."""

    def chat(self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        # Stubbed response – replace with real OpenAI/HF call
        user_last = next((m for m in reversed(messages) if m.get("role") == "user"), {"content": ""})
        content = f"[stub:{model}] You said: {user_last.get('content','')[:500]}"
        return {
            "content": content,
            "usage": {"prompt_tokens": 0, "completion_tokens": len(content.split()), "total_tokens": len(content.split())},
            "model": model,
        }


class EmbeddingProvider:
    """Stub for embedding generation provider."""

    def embed(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        # Deterministic pseudo-embedding for stub
        import hashlib, math
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # produce 64-dim vector
        vec = [(h[i % len(h)] / 255.0) for i in range(64)]
        # L2 normalize
        norm = math.sqrt(sum(v*v for v in vec)) or 1.0
        return [v / norm for v in vec]

    @staticmethod
    def similarity(a: List[float], b: List[float]) -> float:
        # cosine similarity for L2-normalized vectors = dot product
        return float(sum(x*y for x, y in zip(a, b)))


llm_provider = LLMProvider()
embedding_provider = EmbeddingProvider()


# ---- API Views ----
class ChatCopilotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        start = time.time()
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session = None
        if data.get("session_id"):
            try:
                session = ChatSession.objects.get(id=data["session_id"])
            except ChatSession.DoesNotExist:
                return Response({"detail": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            session = ChatSession.objects.create(user=request.user if request.user.is_authenticated else None,
                                                 session_name=data.get("context", {}).get("topic", ""),
                                                 context_metadata=data.get("context", {}))

        # Build message history
        history = [
            {"role": m.role, "content": m.content}
            for m in session.messages.order_by("timestamp").all()
        ]
        history.append({"role": "user", "content": data["message"]})

        # Call LLM provider (stub)
        llm_result = llm_provider.chat(history, model=data.get("model"), temperature=data.get("temperature"), max_tokens=data.get("max_tokens"))
        assistant_text = llm_result["content"]

        # Persist user and assistant messages
        user_msg = ChatMessage.objects.create(session=session, role="user", content=data["message"]) 
        asst_msg = ChatMessage.objects.create(session=session, role="assistant", content=assistant_text)
        session.updated_at = timezone.now()
        session.save(update_fields=["updated_at"]) 

        resp = {
            "response": assistant_text,
            "session_id": str(session.id),
            "message_id": str(asst_msg.id),
            "token_usage": llm_result.get("usage", {}),
            "model": llm_result.get("model"),
            "processing_time": round(time.time() - start, 4),
        }
        return Response(ChatResponseSerializer(resp).data, status=status.HTTP_200_OK)


class EmbedView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        start = time.time()
        serializer = EmbedRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        text = data["text"]
        model = data.get("model")
        vector = embedding_provider.embed(text, model=model)

        # content hash to avoid duplicates
        import hashlib
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        embedding = VectorEmbedding.objects.create(
            content=text,
            content_hash=content_hash,
            embedding_vector=vector,
            embedding_model=model,
            source_type=data.get("source_type"),
            source_id=data.get("source_id") or "",
            metadata=data.get("metadata") or {},
        )

        resp = {
            "embedding_id": str(embedding.id),
            "vector": vector,
            "model": model,
            "token_count": len(text.split()),
            "processing_time": round(time.time() - start, 4),
        }
        return Response(EmbedResponseSerializer(resp).data, status=status.HTTP_201_CREATED)


class SemanticSearchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        start = time.time()
        serializer = SemanticSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        query_vec = embedding_provider.embed(data["query"])  # same default model as stub

        # Base queryset
        qs = VectorEmbedding.objects.all()
        if data.get("source_types"):
            qs = qs.filter(source_type__in=data["source_types"]) 
        # Additional filters
        filters = data.get("filters") or {}
        for key, value in filters.items():
            # Simple equality filters on metadata fields when stored as JSON
            qs = qs.filter(**{f"metadata__{key}": value})

        # Compute similarity in memory for stub (for production use vector DB / pgvector)
        results = []
        top_k = data.get("top_k")
        include_embeddings = data.get("include_embeddings")
        threshold = data.get("threshold")
        for e in qs.iterator():
            sim = EmbeddingProvider.similarity(query_vec, e.embedding_vector)
            if sim >= threshold:
                item = {
                    "content": e.content,
                    "similarity_score": float(sim),
                    "source_type": e.source_type,
                    "source_id": e.source_id,
                    "metadata": e.metadata,
                    "embedding_id": str(e.id),
                }
                if include_embeddings:
                    item["embedding_vector"] = e.embedding_vector
                results.append(item)

        # Sort by similarity desc and trim
        results.sort(key=lambda r: r["similarity_score"], reverse=True)
        results = results[:top_k]

        resp = {
            "results": results,
            "query_embedding": query_vec if include_embeddings else None,
            "total_results": len(results),
            "processing_time": round(time.time() - start, 4),
        }
        return Response(SemanticSearchResponseSerializer(resp).data, status=status.HTTP_200_OK)


class SuggestionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        start = time.time()
        serializer = SuggestionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        context = data["context"]
        types = set((data.get("suggestion_types") or ["workflow", "optimization", "alert", "recommendation"]))
        max_suggestions = data.get("max_suggestions")
        min_conf = data.get("min_confidence")

        # Simple heuristic stub creating suggestions based on context keys
        suggestions: List[ActionSuggestion] = []
        base_candidates = []
        if "errors" in context:
            base_candidates.append({
                "suggestion_type": "alert",
                "title": "Investigate elevated error rates",
                "description": "Error logs indicate anomalies. Propose root-cause analysis and alert thresholds.",
                "priority": "high",
                "confidence_score": 0.82,
            })
        if "latency_ms" in context and context["latency_ms"] > 500:
            base_candidates.append({
                "suggestion_type": "optimization",
                "title": "Optimize slow queries",
                "description": "High latency detected. Suggest indexing, caching, or query optimization.",
                "priority": "medium",
                "confidence_score": 0.75,
            })
        if "todo" in context:
            base_candidates.append({
                "suggestion_type": "workflow",
                "title": "Generate task plan",
                "description": "Convert TODO items into an actionable, prioritized plan.",
                "priority": "medium",
                "confidence_score": 0.7,
            })
        if not base_candidates:
            base_candidates.append({
                "suggestion_type": "recommendation",
                "title": "No obvious issues detected",
                "description": "Monitor metrics and set up automated alerts for thresholds.",
                "priority": "low",
                "confidence_score": 0.6,
            })

        # Filter by requested types and min confidence
        filtered = [c for c in base_candidates if c["suggestion_type"] in types and c["confidence_score"] >= min_conf]
        filtered = filtered[:max_suggestions]

        created_objs = []
        for c in filtered:
            obj = ActionSuggestion.objects.create(
                user=request.user if request.user.is_authenticated else None,
                suggestion_type=c["suggestion_type"],
                title=c["title"],
                description=c["description"],
                priority=c["priority"],
                confidence_score=c["confidence_score"],
                context_data=context,
                action_payload={"proposed_actions": []},
            )
            created_objs.append(obj)

        resp = {
            "suggestions": ActionSuggestionSerializer(created_objs, many=True).data,
            "total_suggestions": len(created_objs),
            "processing_time": round(time.time() - start, 4),
            "context_analysis": {"keys": list(context.keys())},
        }
        return Response(SuggestionResponseSerializer(resp).data, status=status.HTTP_200_OK)


# URL wiring for this microservice will import these views
ChatCopilot = ChatCopilotView.as_view()
Embed = EmbedView.as_view()
SemanticSearch = SemanticSearchView.as_view()
Suggest = SuggestionView.as_view()
