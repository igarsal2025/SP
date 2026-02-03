# Estructura de Documentación - SITEC

**Fecha**: 2026-01-23  
**Versión**: 1.0

---

## 📁 Estructura Propuesta

La documentación está organizada en las siguientes categorías:

```
docs/
├── README.md                    # Índice principal
├── deployment/                  # Guías de deployment
│   ├── PLAN_DEPLOYMENT_RENDER.md
│   ├── GUIA_RAPIDA_RENDER.md
│   ├── CHECKLIST_DEPLOYMENT_RENDER.md
│   └── ...
├── security/                    # Seguridad, MFA, Rate Limiting
│   ├── IMPLEMENTACION_MFA.md
│   ├── IMPLEMENTACION_RATE_LIMITING_AVANZADO.md
│   └── ...
├── testing/                     # Tests y resultados
│   ├── RESULTADOS_TESTS_MFA.md
│   ├── RESULTADOS_TESTS_P0.md
│   └── ...
├── implementation/              # Implementaciones y fases
│   ├── FASE1_IMPLEMENTACION_COMPLETA.md
│   ├── IMPLEMENTACION_P0_COMPLETA.md
│   └── ...
├── guides/                      # Guías de uso
│   ├── GUIA_INICIO_RAPIDO.md
│   ├── MANUAL_OPERACION.md
│   └── ...
├── troubleshooting/            # Solución de problemas
│   ├── TROUBLESHOOTING.md
│   ├── SOLUCION_ERRORES_403.md
│   └── ...
└── summaries/                   # Resúmenes ejecutivos
    ├── RESUMEN_FINAL_P0.md
    ├── RESUMEN_FINAL_MFA.md
    └── ...
```

---

## 🔄 Cómo Organizar

### Opción 1: Script Automático

```powershell
# Ejecutar script de organización
.\scripts\organizar_documentacion.ps1
```

### Opción 2: Manual

Mover archivos manualmente según los patrones:

- **Deployment**: `*DEPLOYMENT*.md`, `*RENDER*.md`
- **Security**: `*MFA*.md`, `*RATE*.md`, `*SEGURIDAD*.md`
- **Testing**: `*TEST*.md`, `*RESULTADOS*.md`, `*VALIDACION*.md`
- **Implementation**: `*FASE*.md`, `*IMPLEMENTACION*.md`, `*P0*.md`
- **Guides**: `*GUIA*.md`, `*MANUAL*.md`, `*INSTRUCCIONES*.md`
- **Troubleshooting**: `*SOLUCION*.md`, `*PROBLEMA*.md`, `*DEBUG*.md`
- **Summaries**: `*RESUMEN*.md`, `*ESTADO*.md`

---

## 📝 Notas

- Los archivos deben estar cerrados para poder moverlos
- Algunos archivos pueden no encajar en categorías (dejar en raíz de `docs/`)
- Actualizar `docs/README.md` después de organizar

---

**Última actualización**: 2026-01-23
