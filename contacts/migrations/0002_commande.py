from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('quantite',      models.PositiveIntegerField(default=1, verbose_name='Quantité')),
                ('statut',        models.CharField(
                    choices=[
                        ('en_attente', 'En attente'),
                        ('confirmee',  'Confirmée'),
                        ('livree',     'Livrée'),
                        ('annulee',    'Annulée'),
                    ],
                    default='en_attente', max_length=20, verbose_name='Statut')),
                ('date_commande', models.DateTimeField(auto_now_add=True,
                                                       verbose_name='Date de commande')),
                ('notes',         models.TextField(blank=True, verbose_name='Notes')),
                ('client', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='commandes',
                    to='contacts.client',
                    verbose_name='Client')),
                ('parfum', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='commandes',
                    to='contacts.parfum',
                    verbose_name='Parfum')),
            ],
            options={
                'verbose_name': 'Commande',
                'verbose_name_plural': 'Commandes',
                'ordering': ['-date_commande'],
            },
        ),
    ]
