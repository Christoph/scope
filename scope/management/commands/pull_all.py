from django.core.management.base import BaseCommand
from scope.methods.dataprovider.provider import Provider

class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument('customer_key', nargs='+', type=str)
        # parser.add_argument(
        #     '--hot', 
        #     dest='hot',
        #     action='store_true',
        #     default=False,
        #     help='Send output to customer',)
        # parser.add_argument(
        #     '--cc', 
        #     dest='cc',
        #     action='store_true',
        #     #nargs='*',
        #     default=False,
        #     help='Send output to admin',)
        # parser.add_argument(
        #     '--print', 
        #     action="store_true",
        #     dest='print',
        #     default=False,
        #     help='Print selected articles to console',)
        # parser.add_argument(
        #     '--db', 
        #     action="store_true",
        #     dest='db',
        #     default=False,
        #     help='Create from database',)

    def handle(self, *args, **options):
        prov = Provider()
        prov.collect_all(out=False)
        


