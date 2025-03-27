# Instanalyze

## Descripción
Instanalyze es una aplicación en Python que procesa un archivo JSON y realiza tareas sobre una cuenta de instagram.

## Estructura del Proyecto
```
mi_app/
│── src/                # Código fuente
│   ├── main.py         # Punto de entrada de la app
│   ├── scraper.py      # Módulo para manejar la web
│   ├── utils.py        # Funciones auxiliares (si es necesario)
│── config.json         # Archivo JSON de configuración
│── requirements.txt    # Dependencias
│── venv/               # Entorno virtual (no se sube a Git)
│── .gitignore          # Ignora archivos innecesarios en Git
│── README.md           # Documentación del proyecto
```

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/usuario/instanalyze.git
   cd instanalyze
   ```

2. Crea un entorno virtual (recomendado):
   ```bash
   python3 -m venv venv
   ```

3. Activa el entorno virtual:
   - En **Mac/Linux**:  
     ```bash
     source venv/bin/activate
     ```
   - En **Windows**:  
     ```bash
     venv\Scripts\activate
     ```

4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para ejecutar la aplicación, estando en la raíz del proyecto, usa el siguiente comando:

```bash
python3 -m src.main
```

## Notas
- El archivo `config.json` contiene datos de configuración, como usuario, contraseña y la URL de la web a analizar.
- Este proyecto usa **Python 3**. Asegúrate de tener Python 3 instalado.
