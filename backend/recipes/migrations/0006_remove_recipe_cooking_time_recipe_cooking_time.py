# Generated by Django 4.0.5 on 2022-07-04 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipe_cooking_time'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipe',
            name='cooking_time',
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.CheckConstraint(check=models.Q(('cooking_time__gte', 1)), name='cooking_time'),
        ),
    ]
