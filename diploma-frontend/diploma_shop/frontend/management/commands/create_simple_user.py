from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        username = ('John', 'Tolik', 'Elma')
        self.stdout.write("Create user")
        for name in username:
            user = User.objects.create_user(username=name, password="123456")
            user.save()
        self.stdout.write(f'Created users {username}')

