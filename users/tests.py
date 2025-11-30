from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Empresa

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
            # Define o endpoint de cadastro (ajuste conforme seu projeto)
            url_cadastro = reverse("user-list")  # Djoser usa esse nome por padrão

            # Tenta cadastrar com o mesmo e-mail já criado no setUp()
            data = {
                "email": self.email,
                "password": "OutraSenha123",
                "name": "Novo Usuário"
            }

            response = self.client.post(url_cadastro, data, format="json")

            # Espera retorno 400 (erro de validação)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("email", response.data)

            # Trata se vier lista ou string
            erro = response.data["email"]
            if isinstance(erro, list):
                erro = erro[0]

            self.assertEqual(erro, "user with this email already exists.")



class AuthTestsSet_us003(APITestCase):
    def setUp(self):
        self.url = reverse("user-list")
        self.email = "usuario2@teste.com"
        self.password = "SenhaSegura123"
        User.objects.create_user(email=self.email, password=self.password, name="Usuário Teste")

    def test_email_limite_maximo_TC012(self):
        max_length_email = 254
        nome_usuario = "a" * (max_length_email - len("@teste.com"))
        email = f"{nome_usuario}@teste.com"
        data = {"email": email, "password": self.password, "name": "Usuário Teste"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_senha_caracteres_especiais_TC0013(self):
        email_base = "usuarioespecial@teste.com"  # variável local
        data = {
            "email": email_base,
            "password": "Senha!@#123",
            "name": "Usuário Especial"
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=email_base).exists())


    def test_case_sensitivity_email_TC0017(self):
        """
        TC0017 - [Validação] Case Sensitivity no cadastro de e-mail.
        O sistema não deve permitir cadastrar um e-mail que difere apenas em maiúsculas/minúsculas.
        """
        email_maiusculas = "Teste@email.com"
        email_minusculas = "teste@email.com"

        # Primeiro cadastro com letras maiúsculas
        data1 = {"email": email_maiusculas, "password": self.password, "name": "Usuário Maiúsculas"}
        response1 = self.client.post(self.url, data1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email__iexact=email_maiusculas).exists())

        # Segundo cadastro com o mesmo e-mail, mas em minúsculas
        data2 = {"email": email_minusculas, "password": self.password, "name": "Usuário Minúsculas"}
        response2 = self.client.post(self.url, data2, format="json")

        # O sistema deve impedir o cadastro duplicado
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response2.data)

        # Pega a mensagem de erro, seja lista ou string
        erro = response2.data["email"]
        if isinstance(erro, list):
            erro = erro[0]

        # Verifica se a mensagem de erro está correta
        self.assertIn("já está cadastrado", str(erro))
    
    def test_nome_caracteres_especiais_TC0018(self):
        """
        TC0018 - [Validação] Nome com caracteres especiais ou números.
        Deve verificar se o sistema aceita ou rejeita nomes com caracteres especiais/números.
        """
        nomes = ["João 123", "Maria!@#", "José Silva"]  # exemplos de teste
        email_base = "usuario_tc018"

        for i, nome in enumerate(nomes):
            with self.subTest(nome=nome):
                email = f"{email_base}{i}@teste.com"
                data = {
                    "email": email,
                    "password": self.password,
                    "name": nome
                }
                response = self.client.post(self.url, data, format="json")

                # Cenário 1: backend permite qualquer caractere no name
                if response.status_code == status.HTTP_201_CREATED:
                    self.assertTrue(User.objects.filter(email=email).exists())

                # Cenário 2: backend valida apenas letras e espaços
                elif response.status_code == status.HTTP_400_BAD_REQUEST:
                    self.assertIn("name", response.data)
                    erro = response.data["name"]
                    if isinstance(erro, list):
                        erro = erro[0]
                    self.assertRegex(
                        str(erro).lower(),
                        r"(nome|inválido|permitido)"
                    )

                else:
                    self.fail(f"Status inesperado {response.status_code} para nome '{nome}'")




class LojaTestsSet_us004(APITestCase):
    def setUp(self):
        # Usuário autenticado para fazer a requisição
        self.admin_user = User.objects.create_user(
            email="admin@teste.com",
            password="Senha123!",
            name="Admin Teste"
        )
        self.client.force_authenticate(user=self.admin_user)

        # Endpoint para criar usuários/lojas
        self.url = reverse("user-list")

        # Primeiro usuário/loja já cadastrado
        self.user_loja1 = User.objects.create_user(
            email="comercial@loja.com",
            password="Senha123!",
            name="Loja 1"
        )

    def test_cnpj_duplicado_TC007(self):
        # Novo usuário tentando usar mesmo CNPJ
        outro_user = User.objects.create_user(
            email="user2@teste.com",
            password="Senha123!",
            name="Outro Usuário",
            documento="12345678000199"  # mesmo CNPJ
        )

        # Autentica o usuário no teste
        self.client.force_authenticate(user=outro_user)

        data = {
            "user": outro_user.id,
            "categoria": 2,
            "descricao": "Outra Loja"
        }

        response = self.client.post(self.url, data, format="json")

        # Espera erro de duplicidade (CNPJ já usado)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user", response.data)

    
    def test_email_duplicado_entre_lojas_TC0015(self):
            """
            TC0015 - Tenta cadastrar uma loja com e-mail já existente.
            Deve retornar erro 400 com mensagem 'Este e-mail já está cadastrado.'
            """
            # Dados do segundo usuário com mesmo e-mail
            data = {
                "email": "comercial@loja.com",  # mesmo e-mail do user_loja1
                "password": "Senha123!",
                "name": "Loja 2"
            }

            # Tenta criar via API
            response = self.client.post(self.url, data, format="json")

            # Deve retornar erro 400
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            # Verifica se a mensagem de erro é sobre e-mail duplicado
            erro = response.data.get("email", [])
            if isinstance(erro, list):
                erro = erro[0]

            self.assertEqual(erro, "user with this email already exists.")

    def test_campos_com_espacos_extras_TC0016(self):
        """
        TC0016 - Verifica se campos com espaços extras são limpos antes do cadastro.
        """
        data = {
            "email": "espacos@loja.com",
            "password": "Senha123!",
            "name": "  Loja Exemplo  "  # espaços extras
        }

        response = self.client.post(self.url, data, format="json")

        # Deve criar com sucesso
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica se os espaços foram removidos
        user = User.objects.get(email="espacos@loja.com")
        self.assertEqual(user.name, "Loja Exemplo")  # espaços removidos

    def test_dados_salvos_corretamente_TC0023(self):
        """
        TC0023 - Verifica se os dados da empresa são persistidos corretamente no banco
        """
        # Cria um usuário para a loja
        user_loja = User.objects.create_user(
            email="dados@loja.com",
            password="Senha123!",
            name="Loja Dados"
        )

        # Endpoint correto para criar empresa/loja
        empresa_url = reverse("empresa-list")

        # Dados da empresa
        data = {
            "user": user_loja.id,
            "categoria": 2,
            "descricao": "Loja Dados Teste"
        }

        # Cria a empresa via API
        response = self.client.post(empresa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica persistência
        empresa = Empresa.objects.get(user=user_loja)
        self.assertEqual(empresa.categoria, 2)
        self.assertEqual(empresa.descricao, "Loja Dados Teste")