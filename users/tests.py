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
        self.assertEqual(str(response.data["detail"][0]), "Email ou Senha incorreta.")

    def test_limite_tentativas_login_TC010(self):
        """
        MUN-6 TC010 - Usuário tenta fazer várias tentativas de login incessantemente.
        Após 5 tentativas inválidas, o sistema deve bloquear temporariamente ou retornar erro apropriado.
        """
        data = {"email": self.email, "password": "SenhaErrada"}
        
        for tentativa in range(6):
            response = self.client.post(self.url, data, format="json")

        # Espera que na 6ª tentativa já seja bloqueado
        self.assertIn(response.status_code, [status.HTTP_429_TOO_MANY_REQUESTS])
        self.assertIn("detail", response.data)

    def test_login_com_senha_antiga_TC011(self):
        """
        MUN-6 TC011 - Login com usuário que alterou a senha recentemente.
        1. Usuário altera a senha.
        2. Tenta logar com a senha antiga.
        Esperado: deve retornar 'Email ou Senha incorreta.'.
        """
        user = User.objects.get(email=self.email)

        # Guarda a senha antiga
        senha_antiga = self.password

        # Altera para uma nova senha
        nova_senha = "NovaSenha@2025"
        user.set_password(nova_senha)
        user.save()

        # Tenta logar com a senha antiga
        data = {"email": self.email, "password": senha_antiga}
        response = self.client.post(self.url, data, format="json")

        # Espera erro 400 com a mensagem personalizada
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)
        self.assertEqual(str(response.data["detail"][0]), "Email ou Senha incorreta.")

    def test_login_conta_bloqueada_TC0012(self):
        """
        MUN-6 TC0012 - Tentativa de login em uma conta bloqueada administrativamente.
        O sistema deve exibir mensagem de erro e impedir o login.
        """
        # Cria um usuário bloqueado
        usuario_bloqueado = User.objects.create_user(
            email="bloqueado@example.com",
            password="SenhaBloqueada123",
            name="Usuário Bloqueado",
            is_active=False  # Conta desativada (bloqueada pelo admin)
        )

        data = {"email": usuario_bloqueado.email, "password": "SenhaBloqueada123"}
        response = self.client.post(self.url, data, format="json")

        # O sistema deve impedir o login
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_401_UNAUTHORIZED
        ])
        self.assertIn("detail", response.data)

        # Trata se for lista ou string
        detail_value = response.data["detail"]
        if isinstance(detail_value, list):
            detail_value = detail_value[0]

        self.assertRegex(
            detail_value.lower(),
            r"(bloquead|suporte|inativo|não\s*permitido)"
        )
    def test_email_duplicado_TC002(self):
        """
        MUN-5 TC002 - [Validação] E-mail Duplicado.
        Deve impedir o cadastro e exibir: "Este e-mail já está cadastrado."
        """
        data = {
            "email": self.email_existente,
            "password": "OutraSenha123",
            "name": "Novo Usuário"
        }

        response = self.client.post(self.url, data, format="json")

        # O sistema deve retornar erro 400
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # Trata se vier lista ou string
        erro = response.data["email"]
        if isinstance(erro, list):
            erro = erro[0]

        self.assertEqual(erro, "Este e-mail já está cadastrado.")