# Generated by Django 3.1.8 on 2021-04-27 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_remove_botconfigurationvariables_auto_cancel_order_after'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.FloatField(editable=False),
        ),
    ]
