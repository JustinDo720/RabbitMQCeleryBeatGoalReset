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
        
        compelted_choices = [
            True, 
            False
        ]

        for i in range(n):
            fake_goal_name = fake.job()
            duration = random.choice(all_duration_options)
            completed = random.choice(compelted_choices)

            create_goal = Goals.objects.create(name=fake_goal_name, completed=completed, duration=duration)
            create_goal.save()

            self.stdout.write(self.style.SUCCESS(f'{fake_goal_name}-{duration}-{completed} successfully added'))

    