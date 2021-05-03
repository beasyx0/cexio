import uuid
from django.db import models
from django.utils import timezone


class TimeStamped(models.Model):
    '''Universal timestamp and UUID public ID'''
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        '''Update timstamps on save'''
        if not self.id:
            self.date = timezone.now()
        self.updated = timezone.now()
        return super(TimeStamped, self).save(*args, **kwargs)


class BotConfigurationVariables(TimeStamped):

    '''
    An object to hold the configuration variables for the bot.

    name: String. A cool name for the bot.

    bot_on: Boolean. Switch to turn the bot on or off.

    pair: String. Market pair to trade with. Ex: 'BTC/USD' or 'ETH/USD'.

    buy: Float. Buys at this percentage below what we bought for.

    upswing_buy: Float. Buys at this percentage if the price goes up intead of down.

    sell: Float. Sells at this percentage above what we bought for.

    downswing_sell: Float. Sells at this percentage if the price goes down instead of up.

    auto_cancel_order_after: Integer. Amount in minutes to wait before auto cancelling orders.
    '''

    PAIR_CHOICES = (
        ('BTC/USD', 'Bitcoin/USDollar'),
        ('ETH/USD', 'Ethereum/USDollar'),
    )

    name = models.CharField(max_length=50)

    bot_on = models.BooleanField(default=False, help_text='Is the bot on?')

    pair = models.CharField(max_length=7, choices=PAIR_CHOICES, help_text='The trade pair')

    buy = models.FloatField(help_text='Percent decrease to trigger buy')

    upswing_buy = models.FloatField(help_text='Percent increase to trigger buy')

    sell = models.FloatField(help_text='Percent increase to trigger sell')

    downswing_sell = models.FloatField(help_text='Percent decrease to trigger sell')

    fee = models.FloatField(default=0.0, help_text='The trade fee in USD')

    auto_cancel_order_period = models.PositiveIntegerField(default=10,
                                    help_text='How long in minutes before auto cancelling')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Bot Configuration Variables'


class Order(TimeStamped):
    '''
    A record of every buy or sell.

    completed: Boolean. Whether or not the order is complete.

    order_id: String. Cex.io order identifier.

    pair: String. Ex: 'BTC/USD' or 'ETH/USD'.

    order_type: Choice. Was this a buy or sell order?

    price: Float. How much we bought or sold the coin for?

    amount: Float. How much total coin was bought or sold?

    total: Float. Total sold or bought for.

    '''

    PAIR_CHOICES = (
        ('BTC/USD', 'Bitcoin/USDollar'),
        ('ETH/USD', 'Ethereum/USDollar'),
    )

    TYPE_CHOICES = (
            ('BUY', 'Buy'),
            ('SELL', 'Sell'),
        )

    order_id = models.CharField(max_length=100, unique=True, help_text='Order ID from CEXIO order')

    pair = models.CharField(max_length=7, choices=PAIR_CHOICES, help_text='Currency pair to trade in')

    order_type = models.CharField(max_length=4, choices=TYPE_CHOICES, help_text='Buying or selling?')

    price = models.FloatField(help_text='Price of coin')

    amount = models.FloatField(help_text='Amount of coin')

    total = models.FloatField(editable=False, help_text='Total USD')

    def __str__(self):
        return f'Order ID: {self.order_id}'

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        '''Update the total depending on the type of order'''
        self.total = self.price * self.amount
        return super(Order, self).save(*args, **kwargs)
