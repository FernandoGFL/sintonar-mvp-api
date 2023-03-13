from django.core.management.base import BaseCommand
from django.db import transaction

from crushonu.apps.crush.models.crush import Crush


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        crushes = Crush.objects.all()

        for crush in crushes:
            if crush.kiss:
                crush_kissed = Crush.objects.filter(
                    user_to=crush.user_from,
                    user_from=crush.user_to,
                    kiss=True,
                )

                if crush_kissed.exists():
                    crush_kissed.update(match=True)

                    crush.match = True
                else:
                    crush.match = False

            else:
                Crush.objects.filter(
                    user_to=crush.user_from,
                    user_from=crush.user_to,
                    kiss=True,
                ).update(match=False)

                crush.match = False

            crush.save()
