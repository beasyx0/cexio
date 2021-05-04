from datetime import datetime, timedelta
import pytz

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import mail_admins
from django.template.loader import render_to_string
from config.celery_app import app

import celery

from cexio.bot.models import BotConfigurationVariables, Order
from cexio.bot.cexio_api import Api


def datetime_aware(dt):
    '''Returns the localized time right now'''
    try:

        timezone = pytz.timezone('America/New_York')
        dt = timezone.localize(dt)
        return dt

    except ValueError:

        return dt


def create_new_local_order(new_order, bot_pair):
    '''Create a new local order'''
    try:
        order_id = new_order['id']
        pair = bot_pair
        order_type = new_order['type'].upper()
        price = float(new_order['price'])
        amount = float(new_order['amount'])
        new_local_order = \
            Order.objects.create(
                order_id=order_id,
                pair=pair,
                order_type=order_type,
                price=price,
                amount=amount,
            )
        print(f'New local order: {new_local_order}')
    except KeyError as e:
        e = f'KeyError: {str(e)}'
        print('sending admin email')
        subject = 'Error Creating Order'
        mail_admins(subject, message=e, fail_silently=False, connection=None, html_message=None)


def notify_of_new_order(new_order):
    '''Email admins on every order'''
    print('notifying of new order')
    subject = 'New ' + new_order['type'] + ' order placed'
    message = 'Amount: ' + str(float(new_order['amount'])) + '\n' + 'Price: ' + str(float(new_order['price']))
    mail_admins(subject, message, fail_silently=False, connection=None, html_message=None)


def notify_of_new_order_error(new_order):
    '''Email admins on new order error'''
    print('notifying of new order error')
    subject = 'New order error'
    message = 'There was an error proccessing an order: ' + new_order['error']
    mail_admins(subject, message, fail_silently=False, connection=None, html_message=None)


def cexio_api_setup():
    '''Initializes api instance for cex.io'''
    username = settings.CEXIO_USERNAME
    key = settings.CEXIO_KEY
    secret = settings.CEXIO_SECRET
    api = Api(username, key, secret)

    return api


@app.task()
def send_daily_report():
    '''A task that runs at intervals and emails admins a summary of the days trades/numbers'''

    api = cexio_api_setup()

    balance = api.balance
    usd_balance = balance['USD']['available']
    btc_balance = balance['BTC']['available']
    eth_balance = balance['ETH']['available']

    now = datetime_aware(datetime.now())
    last_day = datetime_aware(now - timedelta(hours=24))

    last_days_orders = Order.objects.filter(date__gt=last_day).values()

    report_template = 'daily_report_template.txt'

    data = {
        'usd_balance': usd_balance, 
        'btc_balance': btc_balance, 
        'eth_balance': eth_balance, 
        'last_days_orders': last_days_orders, 
        'date': last_day.date()
        }

    subject = ' Daily report'

    daily_report = render_to_string(report_template, data)

    mail_admins(subject, daily_report, fail_silently=False, connection=None, html_message=None)


@app.task()
def cancel_and_delete_open_orders():
    '''
    A task that runs at intervals and checks for open orders.
    If any oders are older than the interval then it gets cancelled
    and deleted.

    1) Check api for open orders
    2) If any, how long were they placed?
    2) Make list of ID's of any open orders placed beyond auto_cancel_order_period
    3) Cancel all these orders on cex api
    4) Verify all orders cancelled on cex api
    5) Make list of local Order objects by order id
    6) Delete all order objects from db
    '''

    bot = get_object_or_404(BotConfigurationVariables, id=1)
    bot_pair = bot.pair
    bot_on = bot.bot_on
    bot_auto_cancel_time = bot.auto_cancel_order_period

    # only run if the bot is on
    if bot_on:

        api = cexio_api_setup()

        # Are there any open orders?
        open_orders = api.open_orders(bot_pair)

        if open_orders:

            local_open_order_ids = []  # orders in our database that match cex.io open orders.. to be deleted..

            for order in open_orders:
                now = datetime.now()
                now_aware = datetime_aware(now)
                cuttoff_time = now_aware - timedelta(minutes=bot_auto_cancel_time)
                order_timestamp = int(order['time']) / 1000  # needs to be int times 1000 for seconds
                order_datetime = datetime.fromtimestamp(order_timestamp)  # datetime object for comparison
                timezone = pytz.timezone('America/New_York')
                order_datetime_aware = timezone.localize(order_datetime)  # order time aware

                if order_datetime_aware < cuttoff_time:  # is it older than auto_cancel_order_period? 
                    # too old, cancel it
                    cancelled = api.cancel_order(order['id'])  # returns True or False
                    if cancelled:
                        local_open_order_ids.append(order['id'])

            if local_open_order_ids:
                # filter with a list of ids
                local_open_orders = Order.objects.filter(order_id__in=local_open_order_ids)
                local_open_orders.delete()


@app.task()
def check_buy_or_sell():
    '''
    A task that runs at intervals and compares the latest coin price
    to the price we paid or recieved on the last Order.

    1) Check if we bought or sold on the last Order to know to either
       buy or sell this time
    2) Get the latest ticker price
    3) Get the price from the last Order for comparison
    4) Use the difference to decide whether to pull the trigger on a
       buy/sell or stop loss (upward_swing_buy/downward_swing_sell)
    '''

    bot = get_object_or_404(BotConfigurationVariables, id=1)
    bot_pair = bot.pair  # hehe
    bot_on = bot.bot_on
    bot_buy = bot.buy
    bot_sell = bot.sell
    bot_fee = bot.fee

    # only run if the bot is on
    if bot_on:

        api = cexio_api_setup()

        # Are there any open orders?
        open_orders_exists = len(api.open_orders(bot_pair)) > 0
        print(f'Open orders? {open_orders_exists}')

        # Only run if no open orders
        if not open_orders_exists:

            last_order = Order.objects.values()[0]
            last_order_type = last_order['order_type']
            last_price = float(api.ticker(bot_pair)['bid'])
            last_price_local = last_order['price']

            # Sell or buy
            if last_order_type == 'BUY':
                # We are looking to SELL. Either for a profit or downswing sell
                sell_price = last_price_local * bot_sell + last_price_local
                downswing_sell_price = last_price_local - (last_price_local * bot.downswing_sell)

                if last_price >= sell_price or last_price <= downswing_sell_price:
                    # We sell our coin balance for a profit or we cut our losses and sell to stop loss
                    coin_balance = api.balance[bot_pair.split('/')[0]]['available']  # all of it

                    new_order = api.sell_limit_order(coin_balance, str(last_price), bot_pair)

                    # Are there any errors with the new order?
                    # If this breaks it runs
                    try:

                        order_error = new_order['error']
                        notify_of_new_order_error(new_order)

                    except KeyError:

                        create_new_local_order(new_order, bot_pair)
                        notify_of_new_order(new_order)

            if last_order_type == 'SELL':
                # We are looking to BUY. Either for cheap coin or upswing buy
                buy_price = round(last_price_local - (last_price_local * bot_buy), 2)
                upswing_buy_price = round(last_price_local * bot.upswing_buy + last_price_local, 2)

                if last_price <= buy_price or last_price >= upswing_buy_price:
                    # We buy our coin cheap or we take a loss and buy the upswing to stop loss
                    usd_balance_minus_fee = float(api.balance[bot_pair.split('/')[-1]]['available']) - bot_fee

                    amount_to_buy = str(round(usd_balance_minus_fee / last_price, 6))  # amount in coin

                    new_order = api.buy_limit_order(amount_to_buy, str(last_price), bot_pair)

                    # Are there any errors with the new order?
                    # If this breaks it runs
                    try:

                        order_error = new_order['error']
                        notify_of_new_order_error(new_order)

                    except KeyError:

                        create_new_local_order(new_order, bot_pair)
                        notify_of_new_order(new_order)
