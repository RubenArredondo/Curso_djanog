from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Vendedor, Lead, Bitacora
from .serializers import VendedorSerializer, LeadSerializer, BitacoraSerializer

# Create your views here.
class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [IsAuthenticated] 

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer
    permission_classes = [IsAuthenticated]

