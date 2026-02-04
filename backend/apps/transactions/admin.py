from django.contrib import admin
from .models import Transaccion, Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['id_transaccion', 'id_cliente', 'monto', 'moneda', 'fecha', 'estado', 'created_at']
    list_filter = ['estado', 'moneda', 'fecha', 'created_at']
    search_fields = ['id_transaccion', 'id_cliente__nombre']
    readonly_fields = ['id_transaccion', 'created_at', 'updated_at']
    date_hierarchy = 'fecha'
    
    fieldsets = (
        ('Información de Transacción', {
            'fields': ('id_transaccion', 'id_cliente', 'fecha', 'estado')
        }),
        ('Detalles Financieros', {
            'fields': ('monto', 'moneda')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
