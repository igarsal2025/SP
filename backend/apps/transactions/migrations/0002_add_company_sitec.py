# Generated migration to add company and sitec fields

from django.db import migrations, models
import django.db.models.deletion


def create_index_if_not_exists(apps, schema_editor):
    """Crear índices solo si no existen, manejando conflictos"""
    db_alias = schema_editor.connection.alias
    connection = schema_editor.connection
    
    # Verificar y crear índice para Cliente si no existe
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='transactions_cliente_company_idx'
        """)
        if not cursor.fetchone():
            try:
                cursor.execute("""
                    CREATE INDEX transactions_cliente_company_idx 
                    ON transactions_cliente (company_id, sitec_id)
                """)
            except Exception as e:
                # Si el índice ya existe por alguna razón, ignorar el error
                if 'already exists' not in str(e).lower() and 'duplicate' not in str(e).lower():
                    raise
    
    # Verificar y crear índice para Transaccion si no existe
    # Primero verificar si existe el índice que causa el conflicto
    with connection.cursor() as cursor:
        # Verificar si existe el índice conflictivo
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='transactions_company_idx'
        """)
        conflicting_index = cursor.fetchone()
        
        # Verificar si existe el índice compuesto que queremos crear
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='transactions_transaccion_company_idx'
        """)
        target_index = cursor.fetchone()
        
        # Si existe el índice conflictivo pero no el que queremos, eliminar el conflictivo y crear el correcto
        if conflicting_index and not target_index:
            try:
                cursor.execute("DROP INDEX IF EXISTS transactions_company_idx")
                cursor.execute("""
                    CREATE INDEX transactions_transaccion_company_idx 
                    ON transactions_transaccion (company_id, sitec_id)
                """)
            except Exception as e:
                # Si el índice ya existe, ignorar el error
                if 'already exists' not in str(e).lower() and 'duplicate' not in str(e).lower():
                    raise
        # Si no existe ninguno, crear el índice compuesto
        elif not target_index:
            try:
                cursor.execute("""
                    CREATE INDEX transactions_transaccion_company_idx 
                    ON transactions_transaccion (company_id, sitec_id)
                """)
            except Exception as e:
                # Si el índice ya existe, ignorar el error
                if 'already exists' not in str(e).lower() and 'duplicate' not in str(e).lower():
                    raise


def reverse_index_creation(apps, schema_editor):
    """Eliminar índices al revertir la migración"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP INDEX IF EXISTS transactions_cliente_company_idx")
        cursor.execute("DROP INDEX IF EXISTS transactions_transaccion_company_idx")


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions_clientes',
                to='companies.company',
                null=True  # Temporal para migración
            ),
        ),
        migrations.AddField(
            model_name='cliente',
            name='sitec',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions_clientes',
                to='companies.sitec',
                null=True  # Temporal para migración
            ),
        ),
        migrations.AddField(
            model_name='transaccion',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions',
                to='companies.company',
                null=True  # Temporal para migración
            ),
        ),
        migrations.AddField(
            model_name='transaccion',
            name='sitec',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions',
                to='companies.sitec',
                null=True  # Temporal para migración
            ),
        ),
        # Hacer los campos no-null después de poblar datos
        migrations.AlterField(
            model_name='cliente',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions_clientes',
                to='companies.company'
            ),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='sitec',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions_clientes',
                to='companies.sitec'
            ),
        ),
        migrations.AlterField(
            model_name='transaccion',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions',
                to='companies.company'
            ),
        ),
        migrations.AlterField(
            model_name='transaccion',
            name='sitec',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='transactions',
                to='companies.sitec'
            ),
        ),
        # Usar RunPython para crear índices de forma segura
        migrations.RunPython(
            create_index_if_not_exists,
            reverse_index_creation,
        ),
    ]
