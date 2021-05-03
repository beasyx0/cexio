from django.test import TestCase
from django.utils import timezone

from cexio.bot.models import TimeStamped, BotConfigurationVariables, Order


class TestModels(TestCase):
    '''Tests for all bot.models'''

    def test_timestamped_save_method(self):
        '''Test model 'TimeStamped' checks that self.date and self.updated updates on save'''

        print('Testing TimeStamped save method')

        timestamped = TimeStamped()
        timestamped.save()
        now = timezone.now()
        timestamped.refresh_from_db()

        self.assertEqual(timestamped.date.date(), now.date())
        self.assertEqual(timestamped.updated.date(), now.date())

        print('Testing complete')

    def test_botconfigurationvariables_str_method_and_fields(self):
        '''Test model 'BotConfigurationVariables' str method'''
        # thest tests need impovement

        print('Testing BotConfigurationVariables str method and fields')

        bot = BotConfigurationVariables(name='Some bot', pair='BTC/USD', buy=0.02, upswing_buy=0.03, 
                                        sell=0.02, downswing_sell=0.03, fee=1.0, auto_cancel_order_period=20)
        bot.save()
        bot.refresh_from_db()

        expected_str = 'Some bot'
        returned_str = bot.__str__()
        self.assertEqual(expected_str, returned_str)

        expected_pair = 'BTC/USD'
        returned_pair = bot.pair
        self.assertEqual(expected_pair, returned_pair)

        expected_buy = 0.02
        returned_buy = bot.buy
        self.assertEqual(expected_buy, returned_buy)

        expected_upswing_buy = 0.03
        returned_upswing_buy = bot.upswing_buy
        self.assertEqual(expected_upswing_buy, returned_upswing_buy)

        expected_sell = 0.02
        returned_sell = bot.sell
        self.assertEqual(expected_sell, returned_sell)

        expected_downswing_sell = 0.03
        returned_downswing_sell = bot.downswing_sell
        self.assertEqual(expected_downswing_sell, returned_downswing_sell)

        expected_fee = 1.0
        returned_fee = bot.fee
        self.assertEqual(expected_fee, returned_fee)

        expected_auto_cancel_order_period = 20
        returned_auto_cancel_order_period = bot.auto_cancel_order_period
        self.assertEqual(expected_auto_cancel_order_period, returned_auto_cancel_order_period)

        print('Testing complete')


    def test_order_str_method(self):
        '''Test model 'Order' str method'''

        print('Testing Order str method')

        order = Order(order_id='123456789', pair='BTC/USD', order_type='BUY', price=55000, amount=0.0001)
        order.save()
        order.refresh_from_db()
        expected_str = 'Order ID: 123456789'
        returned_str = order.__str__()

        self.assertEqual(expected_str, returned_str)

        print('Testing complete')
