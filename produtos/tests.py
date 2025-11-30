from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from produtos.models import Produto
from users.models import Empresa, CategoriaChoices
from django.core.exceptions import ValidationError

User = get_user_model()

class ProdutoPrecoValidationTest(TestCase):
    def setUp(self):
        """Prepara o ambiente para os testes."""
        self.user = User.objects.create_user(
            email='empresa@teste.com',
            password='123',
            name='Minha Empresa',
            usertype=2, 
            documento='12345678901234'
        )
        self.empresa = Empresa.objects.create(
            user=self.user,
            categoria=CategoriaChoices.ALIMENTACAO,
            descricao='Uma ótima empresa de alimentos.'
        )

    def test_valid_price(self):
        """
        TC001: Validação de Preço (R$) - Entrada Válida
        Verifica se um preço válido como '10.50' é aceito e salvo corretamente.
        """
        # Cria um arquivo de imagem em memória para o campo ImageField
        dummy_image = ContentFile(b'dummy_image_content', name='test.jpg')

        produto = Produto.objects.create(
            empresa=self.empresa,
            nome='Produto de Teste',
            descricao='Descrição do produto.',
            preco=Decimal('10.50'),
            quantidade=10,
            imagem=dummy_image
        )

        # Busca o produto no banco para verificar se foi salvo corretamente
        saved_produto = Produto.objects.get(id=produto.id)

        # Verifica se o preço está correto
        self.assertEqual(saved_produto.preco, Decimal('10.50'))

        # A formatação (ex: 'R$ 10,50') é responsabilidade da camada de apresentação (template/serializer),
        # não do modelo. O teste foca em garantir que o valor decimal é armazenado corretamente.

    def test_invalid_price_text(self):
        """
        TC002: Validação de Preço (R$) - Entrada Inválida (Texto)
        Verifica se o sistema impede o salvamento de um produto com um preço não numérico.
        """
        dummy_image = ContentFile(b'dummy_image_content', name='test.jpg')

        produto = Produto(
            empresa=self.empresa,
            nome='Produto com Preço Inválido',
            descricao='Descrição do produto.',
            preco='Dez Reais',  # Preço inválido
            quantidade=5,
            imagem=dummy_image
        )

        with self.assertRaises(ValidationError) as cm:
            produto.full_clean()
        
        # Verifica se a exceção foi lançada para o campo 'preco'
        self.assertIn('preco', cm.exception.message_dict)
        
        # Verifica se a mensagem de erro está correta.
        # A mensagem exata pode variar um pouco entre versões do Django.
        # O importante é checar que a validação falhou com uma mensagem sobre tipo de dado.
        self.assertTrue('must be a decimal number' in cm.exception.message_dict['preco'][0])

    def test_empty_nome_field(self):
        """
        TC005: Campo Obrigatório - Nome do Item
        Verifica se o sistema impede o salvamento de um produto com o campo 'nome' vazio.
        """
        dummy_image = ContentFile(b'dummy_image_content', name='test.jpg')

        produto = Produto(
            empresa=self.empresa,
            nome='',  # Nome do produto vazio
            descricao='Descrição do produto.',
            preco=Decimal('10.50'),
            quantidade=10,
            imagem=dummy_image
        )

        with self.assertRaises(ValidationError) as cm:
            produto.full_clean()
        
        # Verifica se a exceção foi lançada para o campo 'nome'
        self.assertIn('nome', cm.exception.message_dict)
        
        # Verifica se a mensagem de erro indica que o campo é obrigatório
        self.assertTrue('This field cannot be blank.' in cm.exception.message_dict['nome'][0])

    def test_successful_product_creation(self):
        """
        TC007: Criação de Produto - Sucesso
        Verifica se um produto é criado com sucesso com dados válidos.
        """
        initial_product_count = Produto.objects.count()
        dummy_image = ContentFile(b'dummy_image_content', name='test_image.jpg')

        # Criar um produto com dados válidos
        produto = Produto.objects.create(
            empresa=self.empresa,
            nome='Produto Criado com Sucesso',
            descricao='Este é um produto que deve ser criado sem problemas.',
            preco=Decimal('25.99'),
            quantidade=50,
            imagem=dummy_image
        )

        # Verificar se o produto foi salvo no banco de dados
        self.assertIsNotNone(produto.id)
        self.assertEqual(Produto.objects.count(), initial_product_count + 1)

        # Recuperar o produto do banco e verificar seus atributos
        saved_produto = Produto.objects.get(id=produto.id)
        self.assertEqual(saved_produto.nome, 'Produto Criado com Sucesso')
        self.assertEqual(saved_produto.preco, Decimal('25.99'))
        self.assertEqual(saved_produto.quantidade, 50)

    def test_successful_product_deletion(self):
        """
        TC012: Exclusão de Produto - Sucesso e Atualização
        Verifica se um produto é excluído com sucesso e a contagem é atualizada.
        """
        dummy_image = ContentFile(b'dummy_image_content', name='macarons.jpg')

        # Pré-condição: Produto 'Macarons coloridos' cadastrado.
        produto_to_delete = Produto.objects.create(
            empresa=self.empresa,
            nome='Macarons coloridos',
            descricao='Macarons de diversas cores e sabores.',
            preco=Decimal('15.00'),
            quantidade=30,
            imagem=dummy_image
        )

        initial_product_count = Produto.objects.count()

        # 1. Executar a exclusão e confirmar.
        produto_to_delete.delete()

        # O produto 'Macarons coloridos' não deve mais estar na lista.
        self.assertFalse(Produto.objects.filter(id=produto_to_delete.id).exists())

        # A contagem de Total de Produtos deve ser decrementada em 1.
        self.assertEqual(Produto.objects.count(), initial_product_count - 1)

    def test_successful_product_update_multiple_fields(self):
        """
        TC019: Persistência de Edição - Múltiplos Campos
        Verifica se a edição de múltiplos campos de um produto é persistida.
        """
        dummy_image = ContentFile(b'dummy_image_content', name='macarons.jpg')

        # Pré-condição: Produto 'Macarons' com 125 qtd e preço R$ 8,00.
        produto = Produto.objects.create(
            empresa=self.empresa,
            nome='Macarons',
            descricao='Macarons deliciosos.',
            preco=Decimal('8.00'),
            quantidade=125,
            imagem=dummy_image
        )

        # 1. Alterar a Quantidade para 100.
        # 2. Alterar o Preço para R$ 9,50.
        produto.quantidade = 100
        produto.preco = Decimal('9.50')
        
        # 3. Salvar.
        produto.save()

        # Recarregar o produto do banco de dados para garantir que as mudanças foram persistidas
        updated_produto = Produto.objects.get(id=produto.id)

        # Na lista principal, o produto 'Macarons' deve exibir 100 qtd e R$ 9,50.
        self.assertEqual(updated_produto.quantidade, 100)
        self.assertEqual(updated_produto.preco, Decimal('9.50'))