# Generated by Django 5.0.6 on 2024-08-01 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecozone', '0010_psrgeneration_ecozone_psr_start_9c1dfd_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='powerplant',
            name='region_dena',
            field=models.CharField(max_length=2, null=True, verbose_name='Region (dena)'),
        ),
    ]
