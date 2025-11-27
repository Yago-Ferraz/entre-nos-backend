from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Empresa
from .models import Carteira

@receiver(post_save, sender=Empresa)
def create_carteira_for_empresa(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma Carteira para uma nova Empresa.
    """
    if created:
        Carteira.objects.create(empresa=instance)
