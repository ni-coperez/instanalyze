from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from colorama import Fore, Style, init
init(autoreset=True)

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
            print(Fore.YELLOW + "⚠️ Cookies opcionales rechazadas.")
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
        print(Fore.GREEN + "✅ Login completado.")
        
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

                print(Fore.YELLOW + "\n----------------------------------------")
                print(Fore.CYAN + "🔐 Autenticación en dos pasos")
                print(Fore.YELLOW + "----------------------------------------")
                verification_code = input(Fore.WHITE + "Ingresa el código de verificación: ").strip()

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

    def view_profile(self, profile_url):
        """Carga el perfil del usuario en el navegador para revisión manual"""
        full_profile_url = f"https://www.instagram.com/{profile_url}/"
        self.driver.get(full_profile_url)

    # def check_follow_button(self, profile_url):
    #     print(f"Intentando acceder a: https://www.instagram.com/{profile_url}/")
    #     print(f"Estado de sesión antes de acceder: {self.driver.session_id}")  

    #     try:
    #         self.view_profile(profile_url)
    #         time.sleep(3)  # Esperar a que la página cargue completamente
    #         # Buscar el botón de seguir...
    #         button = self.driver.find_element(By.XPATH, "//button[contains(@class, '_acan') and contains(@class, '_acap')]")
    #         print(f"Botón encontrado: {button.text}")
    #         return button.text

    #     except Exception as e:
    #         print(f"Error al intentar obtener el estado del botón: {e}")
    #         return None

    def unfollow_if_requested(self, profile_url):
        try:
            current_url = self.driver.current_url

            if not current_url.rstrip('/').endswith(f"/{profile_url}"):
                self.view_profile(profile_url)
                time.sleep(1)

            # Buscar el botón de seguir
            # Buscar el botón por tipo y luego verificar el texto interno
            buttons = self.driver.find_elements(By.XPATH, "//button[@type='button']")
            follow_button = None
            for btn in buttons:
                try:
                    # El texto del botón está en un div hijo
                    div = btn.find_element(By.XPATH, ".//div[contains(@class, '_ap3a')]")
                    btn_text = div.text.strip()
                    if btn_text in ["Siguiendo", "Seguir", "Solicitado"]:
                        follow_button = btn
                        break
                except Exception:
                    continue
            if not follow_button:
                raise Exception("No se encontró el botón de seguir/solicitar/siguiendo.")

            if follow_button.text == "Solicitado":
                follow_button.click()

                time.sleep(1)  # Esperar un poco para que el diálogo de confirmación aparezca  
                
                # Buscar cualquier elemento clickeable que contenga el texto "Dejar de seguir"
                try:
                    unfollow_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Dejar de seguir')]"))
                    )
                    unfollow_button.click()
                    return True
                except TimeoutException:
                    # Si no aparece el diálogo, verificar si el botón cambió a "Seguir"
                    time.sleep(1)
                    follow_button = self.driver.find_element(By.XPATH, "//button[contains(@class, '_acan') and contains(@class, '_acap')]")
                    if follow_button.text == "Seguir":
                        return True
                    else:
                        return False

            elif follow_button.text == "Seguir":
                return True
            
            elif follow_button.text == "Siguiendo":
                follow_button.click()

                # Buscar cualquier elemento clickeable que contenga el texto "Dejar de seguir"
                try:
                    unfollow_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Dejar de seguir')]"))
                    )
                    unfollow_button.click()
                    return True
                except TimeoutException:
                    # Si no aparece el diálogo, verificar si el botón cambió a "Seguir"
                    time.sleep(1)
                    follow_button = self.driver.find_element(By.XPATH, "//button[contains(@class, '_acan') and contains(@class, '_acap')]")
                    if follow_button.text == "Seguir":
                        return True
                    else:
                        return False

            else:
                return False

        except Exception as e:
            error_message = str(e)
            if "invalid session id" in error_message:
                print("Error: Sesión inválida. Es posible que el navegador haya sido cerrado o la sesión haya expirado.")
                self.close()
                self.login()  # Intentar volver a iniciar sesión
                return False
            else:
                print(f"Error al intentar dejar de seguir: {error_message}")
            return False

    def close(self):
        """Cerrar el navegador"""
        self.driver.quit()