# MANGO Employee v0.13 RC1 — Validation Checklist

## Alcance

- MANGO Meeting Intelligence v2: Skill post-meeting-capture v2.0.0.
- Comando mango meeting con prepare, runtime live o extracción estructurada ya disponible.
- Reporte de tareas, fechas, compromisos, decisiones, pendientes y hasta tres puntos críticos.
- Validación de citas literales; fechas normalizadas en Python.
- Exportación JSON/Markdown y Word/PDF con extras opcionales meeting.
- Compatibilidad de campos con post-meeting-capture v1.
- Sin envíos externos ni promoción automática de Memory.

## Checklist de release

- [x] Canonical Skill, .agents y .claude sincronizadas.
- [x] Fixtures ficticios de transcripción/extracción incluidos.
- [x] README, manual de usuario, especificación técnica y schemas añadidos.
- [x] Compatibilidad con Employee de referencia explícita.
- [x] Release manifest regenerado tras cambios de runtime/especificación.
- [ ] CI Python 3.10–3.13: verificar antes de fusionar.
- [ ] CLI / pruebas DOCX-PDF: verificar en el CI.
- [ ] Confirmar que el manifest comprometido coincide con el generador.
- [ ] Revisar CI del commit de merge en main.

## Provenance

- Format: mango-release-manifest-v1
- Package: 0.13.0rc1
- Canonical files: 32
- Release hash: dd500813ef25e814ea99ab84754e1b5abff05735e752a8e87d29da104b564132

## Límites declarados

Sin transcripción de audio/video, diarización, OCR ni seguimiento externo automático.
Un reporte terminado aún requiere revisión humana; la evidencia literal no
constituye validación independiente de todas las interpretaciones de la IA.
