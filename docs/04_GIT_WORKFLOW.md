# NEBULA-QUANT v1 | Git Workflow

## Rama principal
- main = estable

## Ramas de trabajo
- chore/*
- feature/*
- fix/*
- research/*

## Reglas
1. No trabajar directamente en main
2. Cada bloque importante de trabajo debe vivir en su propia rama
3. Cada commit debe ser claro y trazable
4. Los cambios deben ir acompañados de evidencia o validación

## Flujo recomendado
1. partir desde main actualizada
2. crear rama de trabajo
3. implementar
4. validar
5. commit
6. push
7. merge posterior

## Commits recomendados
- chore: cambios de soporte, documentación, estructura
- feat: nueva funcionalidad
- fix: correcciones
- test: pruebas
- docs: documentación

## Regla de seguridad
Nunca subir:
- .env
- tokens
- apikey_cursor.txt
- logs
- dumps
