from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Sync data from Pennant Student Records and Canvas"

    def add_arguments(self, parser):
        parser.add_argument("schedule_types", nargs="+", type=bool)

    def handle(self, *args, **options):
        for poll_id in options["poll_ids"]:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.stdout.write(
                self.style.SUCCESS('Successfully closed poll "%s"' % poll_id)
            )
