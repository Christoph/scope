from django.core.management.base import BaseCommand

from django.contrib.auth.models import User
from reader.models import User_Reader
# from reader.methods.mail import send_notification
from reader.methods import reader_process

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('key', nargs='+', type=str)
        parser.add_argument(
            '--hot', 
            dest='hot',
            action='store_true',
            default=False,
            help='Send output to customer',)
        parser.add_argument(
            '--cc', 
            dest='cc',
            action='store_true',
            #nargs='*',
            default=False,
            help='Send output to admin',)
        parser.add_argument(
            '--print', 
            action="store_true",
            dest='print',
            default=False,
            help='Print selected articles to console',)
        parser.add_argument(
            '--db', 
            action="store_true",
            dest='db',
            default=False,
            help='Create from database',)

    def handle(self, *args, **options):
        if  options['key'][0] == 'all':
            users = [i.user for i in User_Reader.objects.all()]
        else:
            users = [User.objects.get(username=options['key'][0])]
        for user in users:
                reader = reader_process.Reader(username=user.username)
                if options['db']:
                    selected_articles = reader.from_db()
                else:
                    selected_articles = reader.from_sources()

                if options['print']:
                    print(selected_articles)

                    # send_notification(user.username, options['hot'], options['cc'])
    
                    


