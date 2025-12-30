# Dr. DevLove 
### *o: Cómo aprendí a dejar de analizar y amar escribir cantidades masivas de código*

[![GitHub license](https://img.shields.io/github/license/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code)](https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code/blob/main/LICENSE)

> "¡Caballeros, no pueden pelear aquí! ¡Esta es la Sala de Guerra!" — *Dr. Strangelove*
>
> "¡Desarrolladores, no pueden pensar demasiado aquí! ¡Esto es el IDE!" — *Dr. DevLove*

¿Estás cansado de mirar un cursor parpadeante? ¿Sufres de *Parálisis por Análisis* crónica? ¿Pasas más tiempo planeando tu código que escribiéndolo?

**Dr. DevLove** (alias `gh-stats`) es tu receta. Es una herramienta CLI que prueba que *estás* trabajando. Valida tu existencia rastreando tus contribuciones diarias de código en todo el universo GitHub, sin necesidad de clones locales.

---

[English](./README.md) | [🇨🇳 简体中文](./README.zh-CN.md) | [🇹🇼 繁體中文](./README.zh-TW.md) | [🇯🇵 日本語](./README.ja.md) | [🇰🇷 한국어](./README.ko.md) | [🇪🇸 Español](./README.es.md) | [🇫🇷 Français](./README.fr.md) | [🇸🇦 العربية](./README.ar.md) | [🇮🇳 हिन्दी](./README.hi.md)

---

## 💊 La Receta (Características)

*   **Diagnóstico Remoto**: Escanea tu actividad en GitHub directamente vía API. Sin repositorios locales.
*   **Signos Vitales**: Salida de terminal a color con barras de progreso animadas.
*   **Tratamiento Escalable**: Proyectos personales y organizaciones.
*   **Viaje en el Tiempo**: `today` (hoy), `yesterday` (ayer), `thisweek` (esta semana), `lastweek` (semana pasada), etc.
*   **Recolección de Evidencia**: Exporta todos los mensajes de commit a un archivo Markdown. Ideal para análisis con IA o reportes para tu jefe.
*   **Modo Triage**: Ordena automáticamente los repositorios por fecha de empuje.

## 📥 Ingesta (Instalación)

```bash
brew install gh
gh auth login
gh auth refresh -s read:org  # Obligatorio para organizaciones
```

```bash
git clone https://github.com/forestsheep911/Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code.git
cd Dr-DevLove-or-How-I-Learned-to-Stop-Analysis-Paralysis-and-Love-Writing-Massive-Amounts-of-Code
poetry install
```

## 📋 Dosis (Uso)

```bash
# Verifica que hiciste algo hoy
poetry run gh-stats --range today

# Exporta commits de la semana pasada para resumen con IA
poetry run gh-stats --range lastweek --export-commits
```

### Parámetros

| Flag | Efecto | Defecto |
| :--- | :--- | :--- |
| `--range` | Atajo de fecha (`today`, `yesterday`, `lastweek`, `3days`) | Ninguno |
| `--no-personal` | Excluir repositorios personales | - |
| `--export-commits` | Exporta mensajes a Markdown | False |
| `--all-branches` | Escanea todas las ramas activas | False |

## 📄 Licencia

MIT. Haz lo que quieras, solo escribe código.
