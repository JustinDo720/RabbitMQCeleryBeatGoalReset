from django.core.management.base import BaseCommand
from jb_goal_app.models import Goals

class Command(BaseCommand):
    help = 'Updating the goals based on the duration.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--duration', type=str, help='Specify the duration (Daily, Weekly, Monthly, Yearly)')
    
    # Handling the actual task 
    def handle(self, *args, **kwargs):
        duration = kwargs['duration'].lower()

        # Filter all goals based on duration to find the correct ones
        goals_to_reset = Goals.objects.filter(duration=duration)

        # Updating all records and "resetting" their completed Boolean Field
        goals_to_reset.update(completed=False)
        self.stdout.write(self.style.SUCCESS(f'Successfully reset {goals_to_reset.count()} goals for duration {duration}'))

    