# MANGO Employee v0.13 RC4 — Guided Acceptance Checklist

## Entregables

- [x] Menú en español para instalar/crear Employee, configurar emisor, cotizar,
      analizar reuniones y revisar autorizaciones sin editar JSON.
- [x] Instaladores macOS/Linux y Windows sin permisos de administrador.
- [x] Detección de Python/pip, Word/PDF, Git y runtimes externos opcionales.
- [x] Emisor e impuestos explícitos mediante preguntas, con validación canónica.
- [x] Resumen comercial Decimal antes de confirmar y generar borrador.
- [x] Approval Cards revisadas por separado: Enter no significa aprobación.
- [x] Gate sensitive_data en nuevos Employees y consentimiento antes de
      añadirlo a Employees existentes.
- [x] Prepare genera un prompt privado, no un reporte ficticio.
- [x] Todos los Runs, aprobaciones, folios y trazas usan el control plane existente.
- [x] Manual desde cero, guía de comandos y especificación técnica.

## Verificación antes del merge

- [ ] Tests de Guided, Quote, Meeting, Workflows, Docs y Security.
- [ ] CI Python 3.10, 3.11, 3.12 y 3.13.
- [ ] RELEASE-MANIFEST.json regenerado y coincidente con el generador.
- [ ] CI de main posterior al merge.

## Provenance

Release: 0.13.0rc4
Archivos canónicos: 39
Release hash: 2ee84865656e5778ea5be2116baa973c80999a83dd5517531bc211a1c09e4e54

## Límites

Este release ofrece una experiencia guiada de terminal, no una app web.
Los operadores de CLI no están autenticados con SSO. Los impuestos son
configurados por el emisor y no hay emisión de CFDI, envío de correo,
transcripción de audio ni autorización implícita de información sensible.
