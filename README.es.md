<div align="center">

> **Este documento fue traducido por IA. ¡Las contribuciones son bienvenidas!** · Original: [`README.md`](./README.md) @ `72e6a63`

  <h1>ComfyUI Skill CLI</h1>

  <p><strong>Herramienta de línea de comandos orientada a agentes para gestionar y ejecutar habilidades de flujos de trabajo de ComfyUI.</strong></p>

  <p>
    Cualquier agente de IA que pueda ejecutar comandos de shell (Claude Code, Codex, OpenClaw, etc.) puede usar ComfyUI a través de esta CLI.
  </p>

  <p>
    <a href="https://pypi.org/project/comfyui-skill-cli/"><img src="https://img.shields.io/pypi/v/comfyui-skill-cli?style=flat&color=4F46E5&logo=pypi&logoColor=white" alt="PyPI"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=10B981" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/static/v1?label=Python&message=3.10%2B&color=3B82F6&style=flat&logo=python&logoColor=white" alt="Python 3.10+"></a>
    <a href="https://github.com/HuangYuChuh/ComfyUI_Skill_CLI/stargazers"><img src="https://img.shields.io/github/stars/HuangYuChuh/ComfyUI_Skill_CLI?style=flat&color=EAB308&logo=github" alt="GitHub stars"></a>
  </p>

  <p>
    <a href="#install">Instalación</a> ·
    <a href="#quick-start">Inicio Rápido</a> ·
    <a href="#commands">Comandos</a> ·
    <a href="#for-ai-agents">Para Agentes IA</a>
  </p>

  <p>
    <a href="./README.md">English</a> ·
    <a href="./README.zh.md">简体中文</a> ·
    <a href="./README.zh-TW.md">繁體中文</a> ·
    <a href="./README.ja.md">日本語</a> ·
    <a href="./README.ko.md">한국어</a> ·
    <strong>Español</strong>
  </p>

</div>

---

## ¿Por qué comfyui-skill?

| Capacidad | Por qué importa |
|-----------|-----------------|
| **Nativo para agentes** | Salida JSON estructurada, compatible con pipes, diseñado para ser invocado por agentes de IA |
| **Sin configuración** | Lee `config.json` y `data/` desde el directorio actual, sin necesidad de configuración previa |
| **Ciclo de vida completo** | Descubre, importa, ejecuta, cancela y gestiona flujos de trabajo y dependencias en una sola herramienta |
| **Multi-servidor** | Administra múltiples instancias de ComfyUI y enruta trabajos a distintos equipos de hardware |
| **Descubrimiento de modelos** | Inspecciona carpetas de modelos y nombres de modelos disponibles directamente desde el servidor de destino |
| **Gestión de flota de flujos de trabajo** | Importa, habilita, deshabilita, elimina y migra múltiples flujos de trabajo entre máquinas |
| **Guía de errores** | Los fallos más comunes (OOM, no autorizado, modelos faltantes) devuelven sugerencias accionables |

<a id="install"></a>
## Instalación

```bash
pipx install comfyui-skill-cli
```

O con pip:

```bash
pip install comfyui-skill-cli
```

### Actualización

```bash
pipx upgrade comfyui-skill-cli
```

### Modo de desarrollo

```bash
git clone https://github.com/HuangYuChuh/ComfyUI_Skill_CLI.git
cd ComfyUI_Skill_CLI
pipx install -e .
```

<a id="quick-start"></a>
## Inicio Rápido

```bash
# 1. Ve al directorio de tu proyecto de ComfyUI Skills
cd /path/to/your-skills-project

# 2. Comprueba el estado del servidor
comfyui-skill server status

# 3. Lista los flujos de trabajo disponibles
comfyui-skill list

# 4. Ejecuta un flujo de trabajo
comfyui-skill run local/txt2img --args '{"prompt": "a white cat"}'
```

Todos los comandos admiten `--json` para obtener una salida estructurada.

## Convención de ID

Los flujos de trabajo se identifican como `<server_id>/<workflow_id>`:

```bash
comfyui-skill run local/txt2img          # servidor explícito
comfyui-skill run txt2img                # usa el servidor predeterminado
comfyui-skill run txt2img -s my_server   # sobrescribe con la bandera --server
```

<a id="commands"></a>
## Comandos

### Descubrimiento y Ejecución de Flujos de Trabajo

| Comando | Descripción |
|---------|-------------|
| `comfyui-skill list` | Lista todos los flujos de trabajo disponibles con sus parámetros |
| `comfyui-skill info <id>` | Muestra los detalles del flujo de trabajo y el esquema de parámetros |
| `comfyui-skill run <id> --args '{...}'` | Ejecuta un flujo de trabajo (bloqueante, con streaming en tiempo real por WebSocket) |
| `comfyui-skill run <id> --validate` | Valida el flujo de trabajo sin ejecutarlo |
| `comfyui-skill submit <id> --args '{...}'` | Envía un flujo de trabajo (no bloqueante) |
| `comfyui-skill status <prompt_id>` | Comprueba el estado de ejecución y muestra los resultados encontrados |
| `comfyui-skill cancel <prompt_id>` | Cancela un trabajo en ejecución o en cola |
| `comfyui-skill upload <file>` | Sube un archivo a ComfyUI para usarlo en flujos de trabajo |
| `comfyui-skill upload <file> --mask` | Sube una imagen de máscara para flujos de trabajo de inpainting |
| `comfyui-skill upload --from-output <prompt_id>` | Encadena la salida de una ejecución anterior como entrada para el siguiente flujo de trabajo |

### Gestión de Cola y Recursos

| Comando | Descripción |
|---------|-------------|
| `comfyui-skill queue list` | Muestra los trabajos en ejecución y pendientes |
| `comfyui-skill queue clear` | Elimina todos los trabajos pendientes |
| `comfyui-skill queue delete <prompt_id>...` | Elimina trabajos específicos de la cola |
| `comfyui-skill free` | Libera la memoria de la GPU y descarga los modelos |
| `comfyui-skill free --models` | Solo descarga los modelos |
| `comfyui-skill free --memory` | Solo libera la memoria caché |

### Descubrimiento de Nodos y Modelos

| Comando | Descripción |
|---------|-------------|
| `comfyui-skill nodes list` | Lista todos los nodos de ComfyUI disponibles por categoría |
| `comfyui-skill nodes info <class>` | Muestra el esquema de entradas/salidas de un nodo |
| `comfyui-skill nodes search <query>` | Busca nodos por nombre o categoría |
| `comfyui-skill models list` | Lista todas las carpetas de modelos disponibles |
| `comfyui-skill models list <folder>` | Lista los modelos en una carpeta específica (p. ej., `checkpoints`, `loras`) |

### Gestión de Flujos de Trabajo

| Comando | Descripción |
|---------|-------------|
| `comfyui-skill workflow import <path>` | Importa un flujo de trabajo (detecta el formato automáticamente, genera el esquema automáticamente) |
| `comfyui-skill workflow import --from-server` | Importa uno o más flujos de trabajo desde los datos de usuario del servidor ComfyUI |
| `comfyui-skill workflow enable <id>` | Habilita un flujo de trabajo |
| `comfyui-skill workflow disable <id>` | Deshabilita un flujo de trabajo |
| `comfyui-skill workflow delete <id>` | Elimina un flujo de trabajo |

### Gestión de Servidores

| Comando | Descripción |
|---------|-------------|
| `comfyui-skill server list` | Lista todos los servidores configurados |
| `comfyui-skill server status` | Comprueba si el servidor ComfyUI está en línea |
| `comfyui-skill server stats` | Muestra información de VRAM, RAM y GPU (`--all` para múltiples servidores) |
| `comfyui-skill server add --id <id> --url <url>` | Agrega un nuevo servidor |
| `comfyui-skill server enable/disable <id>` | Activa o desactiva la disponibilidad de un servidor |
| `comfyui-skill server remove <id>` | Elimina un servidor |

### Gestión de Dependencias

| Comando | Descripción |
|---------|-------------|
| `comfyui-skill deps check <id>` | Comprueba nodos personalizados y modelos faltantes |
| `comfyui-skill deps install <id> --all` | Detecta e instala automáticamente todas las dependencias faltantes |
| `comfyui-skill deps install <id> --repos '[...]'` | Instala nodos personalizados específicos |
| `comfyui-skill deps install <id> --models` | Instala los modelos faltantes mediante el Manager |

### Configuración e Historial

| Comando | Descripción |
|---------|-------------|
| `comfyui-skill config export --output <path>` | Exporta la configuración y los flujos de trabajo como un paquete |
| `comfyui-skill config import <path>` | Importa un paquete de configuración (admite `--dry-run`) |
| `comfyui-skill history list <id>` | Lista el historial de ejecuciones |
| `comfyui-skill history show <id> <run_id>` | Muestra los detalles de una ejecución específica |
| `comfyui-skill jobs list` | Lista el historial de trabajos del servidor (`--status` para filtrar) |
| `comfyui-skill jobs show <prompt_id>` | Muestra los detalles de un trabajo específico |
| `comfyui-skill logs show` | Muestra los registros recientes del servidor ComfyUI |
| `comfyui-skill templates list` | Lista las plantillas de flujos de trabajo de nodos personalizados |
| `comfyui-skill templates subgraphs` | Lista los componentes de subgrafos reutilizables |

### Opciones Globales

| Opción | Descripción |
|--------|-------------|
| `--json, -j` | Fuerza la salida en formato JSON |
| `--output-format` | Formato de salida: `text`, `json`, `stream-json` |
| `--server, -s` | Especifica el ID del servidor |
| `--dir, -d` | Especifica el directorio de datos (predeterminado: directorio actual) |
| `--verbose, -v` | Salida detallada |
| `--no-update-check` | Omite la comprobación automática de actualizaciones de la CLI |

### Modos de Salida

| Modo | Cuándo | Formato |
|------|--------|---------|
| Texto | Terminal TTY | Tablas enriquecidas y barras de progreso |
| JSON | Pipe o `--json` | Resultado JSON único |
| Stream JSON | `--output-format stream-json` | Eventos NDJSON en tiempo real |
| Errores | Siempre | stderr |

## Tareas de Gestión Habituales

### Inspeccionar modelos en un servidor

```bash
comfyui-skill models list
comfyui-skill models list checkpoints
comfyui-skill models list loras
```

Úsalo cuando necesites confirmar los nombres de los modelos antes de conectarlos a un flujo de trabajo o esquema.

### Gestionar múltiples flujos de trabajo

```bash
# Previsualiza los flujos de trabajo disponibles en los datos de usuario del servidor ComfyUI
comfyui-skill workflow import --from-server --preview

# Importa los flujos de trabajo que coincidan desde el servidor
comfyui-skill workflow import --from-server --name sdxl

# Deshabilita o vuelve a habilitar temporalmente un flujo de trabajo
comfyui-skill workflow disable local/old-flow
comfyui-skill workflow enable local/old-flow

# Elimina un flujo de trabajo que ya no quieras exponer
comfyui-skill workflow delete local/old-flow
```

### Mover paquetes de flujos de trabajo entre máquinas

```bash
comfyui-skill config export --output ./bundle.json --portable-only
comfyui-skill config import ./bundle.json --dry-run
comfyui-skill config import ./bundle.json --apply-environment
```

Úsalo cuando quieras migrar muchos flujos de trabajo a la vez en lugar de reimportarlos manualmente.

### Comprobar modelos y dependencias antes de ejecutar

```bash
comfyui-skill deps check local/txt2img
comfyui-skill deps install local/txt2img --models
comfyui-skill deps install local/txt2img --all
```

<a id="for-ai-agents"></a>
## Para Agentes IA

Esta CLI está diseñada para ser invocada desde definiciones de `SKILL.md`. Un flujo de trabajo típico de un agente:

```bash
comfyui-skill server status --json                    # 1. verificar servidor
comfyui-skill list --json                             # 2. descubrir flujos de trabajo
comfyui-skill info local/txt2img --json               # 3. comprobar parámetros
comfyui-skill run local/txt2img --args '{...}' --json # 4. ejecutar
```

### Encadenamiento de flujos de trabajo (pipelines de varios pasos)

```bash
# Ejecuta el primer flujo de trabajo
comfyui-skill run local/txt2img --args '{"prompt": "a cat"}' --json

# Encadena la salida al siguiente flujo de trabajo
comfyui-skill upload --from-output <prompt_id> --json
comfyui-skill run local/upscale --args '{"image": "<uploaded_name>"}' --json
```

### Importar y validar

```bash
comfyui-skill workflow import ./workflow.json --check-deps --json
comfyui-skill deps install local/my-workflow --all --json
```

## Contribuciones

¡Las contribuciones son bienvenidas! Por favor, lee la [Guía de Contribución](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw/blob/main/CONTRIBUTING.md) en el repositorio principal para conocer los principios de diseño y el flujo de trabajo de PRs.

## Recursos

- [ComfyUI Skills OpenClaw](https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw) — Repositorio principal de habilidades
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — El backend que esta CLI orquesta
- [Typer](https://typer.tiangolo.com/) — Framework de CLI utilizado por este proyecto

Construido con [Typer](https://typer.tiangolo.com/), el mismo framework que [comfy-cli](https://github.com/Comfy-Org/comfy-cli). Diseñado para integrarse como un subcomando `comfy skills` en el futuro.
