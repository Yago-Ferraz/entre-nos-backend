from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Carteira, Transacao
from .serializers import CarteiraSerializer, TransacaoSerializer, TransacaoInputSerializer
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


class IsOwnerOfCarteira(permissions.BasePermission):
    """
    Permissão customizada para verificar se o usuário autenticado é o dono da carteira.
    Para os casos em que a carteira é implicitamente do usuário (GET/POST em /carteira/, GET em /carteira/transacoes/).
    """
    def has_permission(self, request, view):
        try:
            # Check if the user has an associated carteira.
            # This covers all cases where the carteira is implicitly tied to the user.
            _ = request.user.empresa.carteira 
            return True 
        except (AttributeError, Carteira.DoesNotExist):
            return False


class CarteiraEmpresaView(APIView):
    """
    View para obter os dados da carteira da empresa logada e criar transações para ela.
    """
    permission_classes = [IsAuthenticated, IsOwnerOfCarteira]

    @extend_schema(
        summary="Consultar Carteira da Empresa",
        description="Retorna os saldos em dinheiro e moeda da carteira da empresa associada ao usuário autenticado.",
        responses={
            200: CarteiraSerializer,
            404: {"description": "Nenhuma empresa ou carteira associada a este usuário."}
        }
    )
    def get(self, request):
        user = request.user
        try:
            carteira = user.empresa.carteira
        except AttributeError:
            return Response(
                {"detail": "Nenhuma empresa ou carteira associada a este usuário."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CarteiraSerializer(carteira)
        return Response(serializer.data)

    @extend_schema(
        summary="Criar Transação para a Carteira da Empresa",
        description="Cria uma nova transação para a carteira da empresa associada ao usuário autenticado.",
        request=TransacaoInputSerializer, # Use TransacaoInputSerializer for request body
        responses={
            201: TransacaoSerializer,
            400: {"description": "Dados de transação inválidos ou saldo insuficiente."},
            404: {"description": "Nenhuma empresa ou carteira associada a este usuário."}
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            carteira = user.empresa.carteira
        except AttributeError:
            return Response(
                {"detail": "Nenhuma empresa ou carteira associada a este usuário."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TransacaoInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        valor = serializer.validated_data['valor']
        tipo_ativo = serializer.validated_data['tipo_ativo']
        tipo_operacao = serializer.validated_data['tipo_operacao']
        descricao = serializer.validated_data.get('descricao', '')

        try:
            carteira.registrar_operacao(
                valor=valor,
                tipo_ativo=tipo_ativo,
                tipo_operacao=tipo_operacao,
                descricao=descricao,
                user=user
            )
            # Fetch the latest transaction created by registrar_operacao for response
            latest_transacao = Transacao.objects.filter(carteira=carteira).order_by('-created_at').first()
            if latest_transacao:
                response_serializer = TransacaoSerializer(latest_transacao)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"detail": "Erro ao recuperar a transação após o registro."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': f"Erro ao registrar operação: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransacaoListView(generics.ListAPIView):
    """
    Lista todas as transações da carteira do usuário autenticado.
    """
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfCarteira]

    def get_queryset(self):
        # A permissão IsOwnerOfCarteira já garante que o usuário tem uma carteira.
        # Agora obtemos a carteira do usuário autenticado.
        user_carteira = self.request.user.empresa.carteira
        return Transacao.objects.filter(carteira=user_carteira).order_by('-created_at')

# TransacaoCreateView is removed as its functionality is now in CarteiraEmpresaView.post
