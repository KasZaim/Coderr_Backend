# Generated by Django 5.1.3 on 2024-11-28 10:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coderr_app', '0013_alter_review_unique_together_review_offer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='offer',
        ),
        migrations.RemoveField(
            model_name='review',
            name='reviewer',
        ),
        migrations.AddField(
            model_name='review',
            name='customer_user',
            field=models.ForeignKey(limit_choices_to={'user_profile__type': 'customer'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_reviews', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='review',
            name='business_user',
            field=models.ForeignKey(limit_choices_to={'user_profile__type': 'business'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_reviews', to=settings.AUTH_USER_MODEL),
        ),
    ]