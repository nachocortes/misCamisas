from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Profile

@receiver(post_save, sender=Profile)
def add_usuario_to_cliente_grupo(sender, instance, created, **kwargs):
    if created:
        try:
            grupo1 = Group.objects.get(name='clientes')
        except Group.DoesNotExist:
            grupo1 = Group.objects.create(name='clientes')
            grupo2 = Group.objects.create(name='comerciales')
            grupo3 = Group.objects.create(name='ventas')
            grupo4 = Group.objects.create(name='compras')
            grupo5 = Group.objects.create(name='rrhh')
            grupo6 = Group.objects.create(name='admin')
        instance.user.groups.add(grupo1)