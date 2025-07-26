from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_remove_cliente_status'),
        ('authentication', '0005_alter_usuario_tipo_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='departamento',
            field=models.ForeignKey(
                to='core.departamento',
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                null=True,
                verbose_name='Departamento',
            ),
        ),
    ] 