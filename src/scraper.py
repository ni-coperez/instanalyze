from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class InstagramScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def login(self):
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(2)  # Esperamos un poco para que la página cargue
        
        try:
            # Verificamos si el botón de rechazar cookies opcionales está disponible
            reject_cookies_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Rechazar cookies opcionales')]"))
            )
            reject_cookies_button.click()  # Hacemos clic en el botón para rechazar las cookies
            print("Cookies opcionales rechazadas.")
        except TimeoutException:
            print("No se encontró el botón de cookies opcionales. Continuando con el login.")
        
        # Llenamos el formulario de login
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        time.sleep(5)  # Esperamos unos segundos para asegurarnos de que la página se haya cargado
        print("Login completado.")
        
        # Intentamos encontrar el campo para el código de verificación
        self.handle_verification_code()

    def handle_verification_code(self):
        """
        Maneja la solicitud del código de verificación de dos factores.
        Se solicita hasta 3 veces si el código ingresado es incorrecto o vencido.
        """
        retries = 3
        while retries > 0:
            try:
                # Esperamos a que aparezca el campo del código de seguridad
                verification_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "verificationCode"))
                )
                # Si el código anterior falló, lo borramos
                verification_input.clear()  # Esto borra el contenido del campo de texto

                verification_code = input("Por favor, ingrese el código de seguridad (de la app de autenticación): ")

                # Llenamos el campo con el código ingresado
                verification_input.send_keys(verification_code)

                # Enviamos el formulario para verificar el código
                verification_input.send_keys(Keys.RETURN)
                
                time.sleep(5)  # Esperamos un poco para ver si la verificación es exitosa
                print("Código de seguridad enviado.")
                
                # Verificamos si la verificación fue exitosa
                if self.is_logged_in():
                    print("Inicio de sesión exitoso.")
                    self.handle_save_credentials_prompt()
                    break
                else:
                    print("Código incorrecto o vencido. Intentando nuevamente.")
                    retries -= 1

            except TimeoutException:
                print("No se encontró el campo de código de seguridad. Intentando nuevamente.")
                retries -= 1
                
    def handle_save_credentials_prompt(self):
        """
        Maneja el cartel que aparece después del login preguntando si se desean guardar las credenciales.
        Se hace clic en 'Ahora no' para rechazar el guardado de las credenciales.
        """
        try:
            # Esperamos a que el botón de "Ahora no" esté disponible
            now_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'x1i10hfl') and text()='Ahora no']"))
            )
            now_button.click()  # Hacemos clic en "Ahora no" para no guardar las credenciales
            print("Opción 'Ahora no' seleccionada.")
        except TimeoutException:
            print("No se encontró el cartel de guardar credenciales. Continuando.")

    def is_logged_in(self):
        """
        Verifica si el login fue exitoso.
        Puede ser una comprobación de que estamos en la página de inicio.
        """
        try:
            # Esperamos a que se cargue el perfil o una página similar que indique que el login fue exitoso
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[contains(@alt, 'Foto del perfil de')]"))
            )
            return True
        except TimeoutException:
            return False

    def check_follow_button(self, profile_url):
        print(f"Intentando acceder a: {profile_url}")
        print(f"Estado de sesión antes de acceder: {self.driver.session_id}")  

        try:
            self.driver.get(profile_url)
            print("Página cargada correctamente.")

            # Buscar el botón de seguir...
            button = self.driver.find_element(By.TAG_NAME, "button")
            print(f"Botón encontrado: {button.text}")
            return button.text

        except Exception as e:
            print(f"Error al intentar obtener el estado del botón: {e}")
            return None

    def close(self):
        """Cerrar el navegador"""
        self.driver.quit()