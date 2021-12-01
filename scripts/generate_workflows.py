from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError

from apps.security.models import Workflow


def run(*args):
    if len(args) == 1:
        database = args[0]
        work_flows = [
            {
                'title': 'Roles',
                'url': '/roles',
            },
            {
                'title': 'Usuarios',
                'url': '/users',
            },
            {
                'title': 'Banners',
                'url': '/banners',
            },
        ]

        url_work_flows = []
        for wf in work_flows:
            url_work_flows.append(wf['url'])
            try:
                workflow, created = Workflow.objects.update_or_create(
                    url=wf['url'],
                    defaults={
                        'title': wf['title']
                    },
                )
            except IntegrityError:
                Workflow.objects.using(database).filter(url=wf['url']).delete()
                workflow = Workflow.objects.using(database).create(
                    title=wf['title'], url=wf['url']
                )
            except MultipleObjectsReturned:
                Workflow.objects.using(database).filter(url=wf['url']).delete()
                workflow = Workflow.objects.using(database).create(
                    title=wf['title'], url=wf['url']
                )

        Workflow.objects.using(database).exclude(url__in=url_work_flows).delete()
