# Instanalyze

Instanalyze es una herramienta de terminal para analizar tus datos de Instagram exportados (seguidores, seguidos, solicitudes pendientes, etc.) y automatizar la cancelación de solicitudes o dejar de seguir perfiles desde el navegador usando Selenium.

---

## 🔧 Requisitos

- Python 3.9 o superior (recomendado Python 3.11+)
- Google Chrome instalado
- `chromedriver` (se instala automáticamente con `webdriver-manager`)

---

## 🌐 Exportar tus datos desde Instagram

1. Ir a [https://www.instagram.com/download/request/](https://www.instagram.com/download/request/)
2. Solicita la descarga de tus datos.
3. Cuando recibas el email, descarga el archivo ZIP.
4. Extrae el ZIP y localiza los archivos relevantes dentro de `followers_and_following/`:
   - `followers_1.json`
   - `following.json`
   - `pending_follow_requests.json`
5. Coloca esos archivos dentro de la carpeta `data/` del proyecto.

---

## ⚙️ Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/instanalyze.git
   cd instanalyze
   ```

2. Crear un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Para Windows: venv\Scripts\activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Ejecución

Desde la carpeta `src/`:

```bash
python main.py
```

### Al iniciar:
- Se te pedirá ingresar tu usuario y contraseña.
- Si tenés habilitada la autenticación en dos pasos, se te solicitará el código de tu app de autenticación.

---

## 📋 Opciones del menú

1. **Eliminar solicitudes pendientes**: Recorre las solicitudes que hiciste y permite cancelarlas masivamente o de forma individual.
2. **Eliminar usuarios que sigues pero no te siguen**: Compara los archivos y permite dejar de seguir perfiles que no te siguen. Incluye una `white_list.json` para ignorar perfiles que no quieras dejar de seguir.
3. **Salir**: Finaliza el programa.

---

## 📂 Estructura esperada del proyecto

```
instanalyze/
│
├── data/
│   ├── followers_1.json
│   ├── following.json
│   ├── pending_follow_requests.json
│   └── white_list.json
│
├── src/
│   ├── main.py
│   ├── scraper.py
│   └── data_loader.py
│
├── requirements.txt
└── README.md
```

---

## 🔎 Tips adicionales

- Es recomendable dejar el navegador **visible y enfocado** durante la ejecución.
- Si un botón no aparece, asegurate que la ventana no esté minimizada.
- Podés modificar la `white_list.json` para mantener contactos que no quieras dejar de seguir.

---

## 🚨 Advertencia

Esta herramienta automatiza acciones en Instagram desde tu cuenta. Usala con responsabilidad y moderación para evitar bloqueos temporales por parte de la plataforma.

---

## ✉️ Contribuciones

¡Pull requests, mejoras de estilo o nuevas features son bienvenidas!
