from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()
class AuthTests(APITestCase):
    def setUp(self):
        # usuário válido já cadastrado no sistema
        self.email = "usuario@teste.com"
        self.password = "senhasegura123"
        User.objects.create_user(email=self.email, password=self.password, name="Usuário Teste")

        # endpoint do djoser/simplejwt
        self.url = reverse("token_obtain_pair")  # /api/auth/jwt/create/
    def test_usuario_nao_cadastrado_tenta_login_TC003(self):
        """
        TC003 - Usuário não cadastrado tenta fazer login.
        Deve retornar a mensagem: 'Preencha o campo matrícula.'
        """
        url = reverse("token_obtain_pair")  # /api/auth/jwt/create/
        data = {
            "email": "naoexiste@example.com",
            "password": "qualquercoisa"
        }

        response = self.client.post(url, data, format="json")

        # Valida retorno
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(str(response.data["detail"][0]), "Email ou Senha incorreta.")

    def test_sql_injection_no_campo_senha_TC009(self):
        """
        MUN-6 TC009 - Realizar login usando códigos SQL no campo de senha.
        O sistema não deve executar o comando e deve tratar a entrada como texto.
        """
        data = {
            "email": self.email,
            "password": "' OR '1'='1"
        }
        response = self.client.post(self.url, data, format="json")

        # O sistema deve falhar no login (não executar o SQL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(str(response.data["detail"][0]), "Email ou Senha incorreta .")


