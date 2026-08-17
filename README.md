# ai-skills

## Qué es este repositorio

Este es un repositorio compartido de skills para agentes de inteligencia artificial.

No está vinculado exclusivamente a Codex. Las skills pueden ser utilizadas por cualquier agente que permita cargar instrucciones, skills, rules o mecanismos equivalentes.

El catálogo contiene las skills y la documentación necesaria para que cada agente pueda incorporarlas usando su propio mecanismo de instalación o configuración.

## Cómo utilizarlo

Clona el repositorio:

```bash
git clone https://github.com/cayetanoherman/ai-skills.git
```

Después tendrás todas las skills disponibles dentro de:

```text
skills/
```

## Cómo instalar una skill

Este repositorio no incluye ningún instalador propio. Abre el agente de IA que estés utilizando y pídele que lea la carpeta de la skill y la instale mediante el mecanismo oficial de ese agente.

Por ejemplo:

```text
Instala para el agente que estoy utilizando actualmente la siguiente skill:

/ruta/al/repositorio/ai-skills/skills/refactor-unificar-paqueteria-proyectos-java

Analiza su contenido y utiliza el mecanismo oficial de instalación/configuración de skills de este agente.
```

### Responsabilidad del agente

Será el propio agente quien deberá:

1. Leer la skill.
2. Detectar cuál es su mecanismo de skills o instrucciones.
3. Instalarla en la ubicación adecuada.
4. Adaptarla únicamente si el formato del agente lo requiere.
5. No modificar la skill original almacenada en este repositorio.

## Actualización del repositorio

Para obtener las últimas skills:

```bash
git pull
```

## Añadir nuevas skills

Añade cada nueva skill como una carpeta independiente directamente dentro de:

```text
skills/
```

Por ejemplo:

```text
skills/
├── skill-a/
│   └── SKILL.md
├── skill-b/
│   └── SKILL.md
└── skill-c/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

Cada skill debe conservar todos los archivos que necesite, incluidos `SKILL.md`, scripts, referencias, ejemplos y cualquier otro recurso requerido.

