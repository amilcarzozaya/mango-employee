# MANGO Meeting Intelligence v2.0.0

Evolución de la Skill canónica `post-meeting-capture` incluida en MANGO Employee.

Convierte transcripciones/minutas en reportes con tareas, fechas, decisiones,
compromisos, pendientes y hasta tres asuntos críticos. Todos los elementos
estructurados exigen citas literales; un motor Python valida citas, normaliza
fechas y exporta documentos. La IA no emite documentos directamente.

## Inicio rápido

Sin modelo externo, utiliza el ejemplo ficticio:

```bash
python -m pip install -e ".[meeting]"
mango meeting reference-employees/mango-chief-of-staff \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md,docx,pdf \
  --out-dir ./reportes
```

Con un modelo configurado, omite `--extraction` e indica `--runtime codex`
u otro runtime compatible. `--runtime prepare` solo prepara el prompt y no
fabrica resultados.

## Seguridad

No envía correos, no programa tareas, no modifica CRM, no promueve Memory.
Los reportes son borradores para revisión humana; conserva el material
sensible sólo en ubicaciones autorizadas.

## Documentación

- `docs/meeting-intelligence/USER-GUIDE.md`
- `docs/meeting-intelligence/TECHNICAL-SPEC.md`
- `extraction.schema.json`
