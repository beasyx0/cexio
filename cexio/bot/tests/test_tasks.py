from django.test import TestCase
from django.core import mail

from cexio.bot.tasks import create_new_local_order, notify_of_new_order, send_daily_report
from cexio.bot.models import Order


class TestTasks(TestCase):
    '''Test the bot tasks'''

    def test_create_new_local_order_and_notify_of_new_order(self):
        '''Test that we can create a new order create_new_local_order_task'''

        # create_new_local_order
        new_order = {
            'id': '9999999999',
            'type': 'sell',
            'price': '54000.0',
            'amount': '0.0012000'
            }

        bot_pair = 'BTC/USD'

        new_local_order = create_new_local_order(new_order, bot_pair)

        saved_order = Order.objects.get(order_id=new_order['id'])

        self.assertEqual(saved_order.order_id, new_order['id'])
        self.assertEqual(saved_order.order_type.lower(), new_order['type'])
        self.assertEqual(saved_order.price, float(new_order['price']))
        self.assertEqual(saved_order.amount, float(new_order['amount']))

        # notify_of_new_order
        notify_of_new_order(new_order)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Django] ' + 'New ' + new_order['type'] + ' order placed')

    def test_send_daily_report(self):
        '''Test that we can send the daily report using the task'''
        
        report = send_daily_report()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, '[Django] Daily report')
