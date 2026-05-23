from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EcoFact, EducationalContent
from .serializers import EcoFactSerializer, EducationalContentSerializer


class EducationalContentListView(generics.ListAPIView):
    serializer_class = EducationalContentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = EducationalContent.objects.filter(is_published=True).order_by("order")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs


class EducationalContentDetailView(generics.RetrieveAPIView):
    queryset = EducationalContent.objects.filter(is_published=True)
    serializer_class = EducationalContentSerializer
    permission_classes = [AllowAny]


class RandomEcoFactView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        fact = EcoFact.objects.order_by("?").first()
        if fact is None:
            return Response({})
        return Response(EcoFactSerializer(fact).data)
