# Generated by Django 4.0.5 on 2022-06-22 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_recipe_cooking_time_remove_recipe_tags_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='ingridients',
            new_name='ingredients',
        ),
    ]
