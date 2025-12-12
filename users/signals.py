#
# Project: SigetsopProject
# Copyrigtht (C) 2025 marconina999@gmail.com. All rights reserveds.
# Unauthorized copyng or distribution prohibited.
#
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import CustomUser, Role


DEFAULT_ROLES = [
    {"name": "Admin", "description": "Super User of system"},
    {"name": "Auxiliar", "description": "AUXILIAR DE UNA UNIDAD"},
    {"name": "AuxiliarSIT", "description": "AUXILIAR DEL SIT Y BAJAS"},
    {"name": "PersonalTS", "description": "PERSONAL TRABAJO SOSIAL"},
    {"name": "Archivos", "description": "ENCARGADO DE KARDEX Y ARCHIVOS"},
    {"name": "Invitado", "description": "Usuario con acceso de solo lectura"},
]


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name != "users":
        return

    # NOTE:  Crear todos los roles por defecto
    admin_role = None
    print("\n📦 Creando/Verificando Roles por defecto...")

    for role_data in DEFAULT_ROLES:
        # Usa .get_or_create para crear el rol solo si no existe
        role, created = Role.objects.get_or_create(
            name=role_data["name"], defaults={"description": role_data["description"]}
        )

        if created:
            print(f"   ✅ Rol '{role.name}' creado.")

        # Guardamos la referencia del rol 'Admin' para el superusuario
        if role.name == "Admin":
            admin_role = role

    # NOTE: Crear usuario admin si no existe ninguno
    # Usamos CustomUser.objects.filter(is_superuser=True).exists() para buscar un superusuario
    if not CustomUser.objects.filter(is_superuser=True).exists():
        if admin_role:
            CustomUser.objects.create_superuser(
                username="nina",
                email="marconina999@gmail.com",
                password="nina1234",
                role=admin_role,
            )
            print(
                "👤 Usuario 'nina' (SuperAdmin) creado con contraseña por defecto 'nina1234'."
            )
        else:
            print(
                "⚠️ No se pudo crear el SuperUsuario: el rol 'Admin' no fue encontrado."
            )
    else:
        print("⏭️ Ya existe un SuperUsuario. Omite la creación.")

    print("✅ Proceso de post_migrate para 'users' completado.\n")
