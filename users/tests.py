from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()
class AuthTests(APITestCase):
    def setUp(self):
        # usuário válido já cadastrado no sistema
        self.email = "usuario@teste.com"
        self.password = "SenhaSegura123"
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

        
    def test_sql_injection_no_campo_email_nao_deve_autenticar_TC007(self):
        """
        TC007 - Realizar login usando códigos SQL no campo de email:
        O sistema deve tratar a entrada como texto e não executar SQL, resultando em falha de login.
        """
        # payload de injeção clássico (tentativa de 'bypass')
        injection_payloads = [
            "' OR '1'='1",
            "' OR '1'='1' -- ",
            "'; DROP TABLE users_user; --",
            "test@example.com' OR 1=1 --"
        ]

        for payload in injection_payloads:
            with self.subTest(payload=payload):
                data = {"email": payload, "password": "qualquer"}
                response = self.client.post(self.url, data, format="json")

                # Deve falhar o login (SimpleJWT/Djoser costuma retornar 400 em validação)
                self.assertIn(response.status_code, (status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED))

                # Não deve retornar tokens
                self.assertNotIn("access", response.data)
                self.assertNotIn("refresh", response.data)

                # Mensagem de erro presente (não checamos conteúdo exato para não acoplar demais,
                # mas você pode exigir a mensagem específica do seu serializer se quiser)
                self.assertTrue("detail" in response.data or any(isinstance(v, list) for v in response.data.values()))

        # Confirma que o banco de usuários não foi alterado (ainda existe só 1 usuário criado no setUp)
        self.assertEqual(User.objects.count(), 1)
