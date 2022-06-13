from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError

from apps.security.models import Workflow, Module, Role, User


def run(*args):
    if len(args) == 1:
        database = args[0]
        work_flows = [
            # Administracion de sistemas
            {
                'module': 'Administración de Sistema',
                'icon': 'system_update_outlined',
                'workflows': [
                    {
                        'title': 'Configuración',
                        'url': 'settings',
                        'icon': 'settings_display'
                    },
                    {
                        'title': 'Gestión de Usuarios',
                        'url': 'users',
                        'icon': 'supervised_user_circle_rounded'
                    },
                    {
                        'title': 'Gestión de Roles',
                        'url': 'roles',
                        'icon': 'accessibility_rounded'
                    },
                    {
                        'title': 'Gestión de Sucursales',
                        'url': 'branch_offices',
                        'icon': 'accessibility_rounded'
                    },
                    {
                        'title': 'Gestión de Sucursales',
                        'url': 'branch_offices',
                        'icon': 'location_city_outlined'
                    },
                    {
                        'title': 'Gestión de Usos',
                        'url': 'uses',
                        'icon': 'verified_outlined'
                    },
                    {
                        'title': 'Gestión de Planes',
                        'url': 'plans',
                        'icon': 'local_offer_outlined'
                    },
                    {
                        'title': 'Gestión de Coberturas',
                        'url': 'coverages',
                        'icon': 'local_convenience_store_sharp'
                    },
                    {
                        'title': 'Gestión de Primas',
                        'url': 'premiums',
                        'icon': 'price_change_outlined'
                    },
                    {
                        'title': 'Gestión de Clientes',
                        'url': 'clients',
                        'icon': 'supervised_user_circle_outlined'
                    },
                    {
                        'title': 'Gestión de Asesores',
                        'url': 'advisers',
                        'icon': 'supervisor_account'
                    },
                    {
                        'title': 'Gestión de Pólizas',
                        'url': 'policies',
                        'icon': 'security_update_good_outlined'
                    },
                ]
            },

            # Administración Web
            {
                'module': 'Administración Web',
                'icon': 'web_outlined',
                'workflows': [
                    {
                        'title': 'Gestión de Banners',
                        'url': 'banners',
                        'icon': 'nature',
                    },
                    {
                        'title': 'Gestión de Secttions',
                        'url': 'sections',
                        'icon': 'home_repair_service_outlined',
                    },
                ]
            },

            # Administración de Vehículos
            {
                'module': 'Administración de Vehículos',
                'icon': 'car_rental_outlined',
                'workflows': [
                    {
                        'title': 'Gestión de Marcas',
                        'url': 'marks',
                        'icon': 'image_outlined',
                    },
                    {
                        'title': 'Gestión de Modelos',
                        'url': 'models',
                        'icon': 'model_training_outlined',
                    },
                    {
                        'title': 'Gestión de Vehículos',
                        'url': 'vehicles',
                        'icon': 'car_repair_outlined',
                    },
                ]
            },

            # Administración de Pagos
            {
                'module': 'Administración de Pagos',
                'icon': 'payment_outlined',
                'workflows': [
                    {
                        'title': 'Gestión de Bancos',
                        'url': 'banks',
                        'icon': 'food_bank_outlined',
                    },
                    {
                        'title': 'Gestión de Pagos',
                        'url': 'payments',
                        'icon': 'payment_outlined',
                    },
                ]
            }
        ]

        workflows_p = []
        url_work_flows = []
        mods = []
        for mod in work_flows:
            module, created = Module.objects.using(database).get_or_create(
                title=mod['module'],
                icon=mod['icon']
            )
            mods.append(module.title)
            for wf in mod['workflows']:
                url_work_flows.append(wf['url'])
                try:
                    workflow, created = Workflow.objects.using(database).update_or_create(
                        url=wf['url'],
                        defaults={
                            'module_id': module.id,
                            'title': wf['title'],
                            'icon': wf['icon']
                        },
                    )
                except IntegrityError:
                    Workflow.objects.using(database).filter(url=wf['url']).delete()
                    workflow = Workflow.objects.using(database).create(
                        title=wf['title'], url=wf['url'], module_id=module.id, icon=wf['icon']
                    )
                except MultipleObjectsReturned:
                    Workflow.objects.using(database).filter(url=wf['url']).delete()
                    workflow = Workflow.objects.using(database).create(
                        title=wf['title'], url=wf['url'], module_id=module.id, icon=wf['icon']
                    )
                workflows_p.append(workflow)

        Workflow.objects.using(database).exclude(url__in=url_work_flows).delete()
        Module.objects.using(database).exclude(title__in=mods).delete()

        role, created = Role.objects.get_or_create(name='Admin')
        role.workflows.set(workflows_p)
        role.save()

        for user in User.objects.filter(is_superuser=True):
            user.roles.set([role])
            user.save()
