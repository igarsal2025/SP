import uuid
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

from apps.companies.models import Company, Sitec


class Cliente(models.Model):
    """Modelo de cliente para las transacciones"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='transactions_clientes',
        null=False,
        blank=False
    )
    sitec = models.ForeignKey(
        Sitec,
        on_delete=models.CASCADE,
        related_name='transactions_clientes',
        null=False,
        blank=False
    )
    nombre = models.CharField(max_length=200, null=False, blank=False)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions_cliente'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['company', 'sitec']),
        ]

    def __str__(self):
        return self.nombre


class Transaccion(models.Model):
    """
    Modelo de transacción financiera con validaciones estrictas de integridad.
    
    Campos:
    - id_transaccion: Identificador único de la transacción (UUID)
    - id_cliente: Referencia al cliente (ForeignKey)
    - monto: Monto de la transacción (Decimal, debe ser positivo)
    - moneda: Código de moneda ISO 4217 (3 caracteres)
    - fecha: Fecha y hora de la transacción
    - estado: Estado de la transacción (pendiente, completada, cancelada, fallida)
    """
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('fallida', 'Fallida'),
    ]
    
    MONEDAS_VALIDAS = [
        'MXN', 'USD', 'EUR', 'GBP', 'CAD', 'ARS', 'BRL', 'CLP', 'COP', 'PEN',
    ]
    
    id_transaccion = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_column='id_transaccion',
        verbose_name='ID Transacción'
    )
    
    id_cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,  # Proteger contra eliminación accidental
        related_name='transacciones',
        db_column='id_cliente',
        verbose_name='Cliente',
        null=False,
        blank=False
    )
    
    monto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],  # Mínimo 0.01
        verbose_name='Monto',
        help_text='Monto de la transacción (debe ser mayor a 0)'
    )
    
    moneda = models.CharField(
        max_length=3,
        choices=[(m, m) for m in MONEDAS_VALIDAS],
        default='MXN',
        verbose_name='Moneda',
        help_text='Código ISO 4217 de la moneda (3 caracteres)'
    )
    
    fecha = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha',
        help_text='Fecha y hora de la transacción'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado',
        db_index=True  # Índice para búsquedas frecuentes
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='transactions',
        null=False,
        blank=False
    )
    sitec = models.ForeignKey(
        Sitec,
        on_delete=models.CASCADE,
        related_name='transactions',
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions_transaccion'
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha', '-created_at']
        indexes = [
            models.Index(fields=['company', 'sitec']),
            models.Index(fields=['id_cliente', '-fecha'], name='transaccion_cliente_fecha_idx'),
            models.Index(fields=['estado', '-fecha'], name='transaccion_estado_fecha_idx'),
            models.Index(fields=['moneda', '-fecha'], name='transaccion_moneda_fecha_idx'),
            models.Index(fields=['-fecha'], name='transaccion_fecha_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(monto__gt=0),
                name='transaccion_monto_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(estado__in=['pendiente', 'completada', 'cancelada', 'fallida']),
                name='transaccion_estado_valido'
            ),
        ]
    
    def clean(self):
        """Validaciones adicionales a nivel de modelo"""
        super().clean()
        
        # Validar que el monto sea positivo (solo si está definido)
        if self.monto is not None and self.monto <= 0:
            raise ValidationError({
                'monto': 'El monto debe ser mayor a 0'
            })
        
        # Validar que la moneda sea válida
        if self.moneda not in self.MONEDAS_VALIDAS:
            raise ValidationError({
                'moneda': f'Moneda inválida. Debe ser una de: {", ".join(self.MONEDAS_VALIDAS)}'
            })
        
        # Validar que el estado sea válido
        if self.estado not in dict(self.ESTADO_CHOICES).keys():
            raise ValidationError({
                'estado': f'Estado inválido. Debe ser uno de: {", ".join(dict(self.ESTADO_CHOICES).keys())}'
            })
        
        # Validar que la fecha no sea futura (opcional, según reglas de negocio)
        if self.fecha > timezone.now():
            raise ValidationError({
                'fecha': 'La fecha de la transacción no puede ser futura'
            })
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para ejecutar validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Transacción {self.id_transaccion} - Cliente: {self.id_cliente.nombre} - {self.monto} {self.moneda}"
