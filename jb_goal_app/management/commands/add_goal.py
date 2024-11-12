from django.core.management.base import BaseCommand
from jb_goal_app.models import Goals
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Adding Goals based on numbers'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', type=int, help='Amount of Goals being added')
    
    def handle(self, *args, **options):
        fake = Faker()
        n = options.get('number') or 1

        all_duration_options = [
                'daily',
                'weekly',
                'monthly',
                'yearly',
            ]
        
        for i in range(n):
            fake_goal_name = fake.job()
            duration = random.choice(all_duration_options)
            # It's better to automatically set completed as True because we're testing out our scheduling (cel and cel beat)
            create_goal = Goals.objects.create(name=fake_goal_name, completed=True, duration=duration)
            create_goal.save()

            self.stdout.write(self.style.SUCCESS(f'{fake_goal_name}-{duration}-{create_goal.completed} successfully added'))

    