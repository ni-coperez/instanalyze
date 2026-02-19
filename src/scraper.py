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
        self.driver.get("https://www.instagram.com/")
        wait = WebDriverWait(self.driver, 20)

        # --- Manejo de cookies ---
        try:
            cookies_button = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(text(),'Permitir todas las cookies') or contains(text(),'Rechazar cookies opcionales')]"
                ))
            )
            cookies_button.click()
            print(Fore.YELLOW + "⚠️ Modal de cookies gestionado.")
            time.sleep(2)
        except TimeoutException:
            print("No apareció el modal de cookies.")

        # --- Esperar inputs de login (nuevo DOM Instagram) ---
        username_input = wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        password_input = wait.until(
            EC.presence_of_element_located((By.NAME, "pass"))
        )

        time.sleep(1)
        username_input.clear()
        username_input.send_keys(self.username)

        time.sleep(1)
        password_input.clear()
        password_input.send_keys(self.password)

        # --- Botón Iniciar sesión (nuevo formato div role=button) ---
        login_button = wait.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@role='button']//span[text()='Iniciar sesión']/ancestor::div[@role='button']"
            ))
        )

        time.sleep(2)
        login_button.click()

        time.sleep(5)
        print(Fore.GREEN + "✅ Login enviado.")

        # Intentar manejar 2FA si aparece
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

    def hide_stories(self):
        """
        Permite ocultar o mostrar las historias para una lista de usuarios especificados en un archivo JSON.
        """
        import json

        action_input = input("¿Qué deseas hacer? (o = ocultar / m = mostrar historias): ").strip().lower()
        if action_input not in ["o", "m"]:
            print("Acción no válida. Usa 'o' para ocultar o 'm' para mostrar.")
            return
        action = "ocultar" if action_input == "o" else "mostrar"

        try:
            with open("custom/hide_story.json", "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception as e:
            print(f"No se pudo cargar el archivo JSON: {e}")
            return

        self.driver.get("https://www.instagram.com/accounts/hide_story_and_live_from/")
        time.sleep(3)

        for user in users:
            username = user.get("value")
            if not username:
                continue

            try:
                search_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Buscar']"))
                )
                search_input.clear()
                search_input.send_keys(username)
                time.sleep(2)

                # Esperamos a que aparezca el resultado de búsqueda
                result = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, f"//span[text()='{username}']"))
                )

                # Subimos al div contenedor del usuario para encontrar el botón asociado al checkbox
                user_container = result.find_element(By.XPATH, "./ancestor::div[contains(@style,'justify-content: space-between')]")
                checkbox = user_container.find_element(
                    By.XPATH,
                    ".//div[@role='button' and @aria-label='Activar o desactivar casilla']"
                )

                # Determinar si está seleccionado por el color de fondo del icono
                icon_div = checkbox.find_element(
                    By.XPATH,
                    ".//div[@data-bloks-name='ig.components.Icon']"
                )
                style = icon_div.get_attribute("style") or ""
                is_selected = "background-color: rgb(0, 149, 246)" in style
                is_unselected = "background-color: rgb(54, 54, 54)" in style

                should_click = (
                    (action == "ocultar" and not is_selected) or
                    (action == "mostrar" and is_selected)
                )
                if should_click:
                    # Usar JS para evitar problemas de pointer-events
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    print(f"{action.capitalize()} historias para: {username}")
                else:
                    print(f"Ya estaba en el estado deseado: {username}")
                time.sleep(30)

            except Exception as e:
                print(f"No se pudo procesar {username}: {e}")
                time.sleep(30)

    def remove_current_close_friends(self):
        """
        Elimina todos los usuarios actuales de la lista de mejores amigos.
        Se detiene al encontrar el primer usuario que ya no está seleccionado.
        """
        from selenium.webdriver.common.action_chains import ActionChains

        print("Accediendo a la configuración de Mejores Amigos...")
        self.driver.get("https://www.instagram.com/accounts/close_friends/")
        time.sleep(3)

        try:
            # Nueva lógica: buscamos los span de nombres de usuario dentro de botones válidos, y subimos al contenedor botón
            items = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@role='button' and @tabindex='0']//span"))
            )
            # Subir al contenedor del usuario (el botón) desde el span
            items = [span.find_element(By.XPATH, "./ancestor::div[@role='button']") for span in items]

            for index, item in enumerate(items):
                try:
                    checkbox_icon = item.find_element(By.XPATH, ".//div[contains(@style, 'background-color')]")
                    is_selected = "rgb(0, 149, 246)" in checkbox_icon.get_attribute("style")

                    if is_selected:
                        # Scroll to the item before clicking
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                        time.sleep(0.5)

                        print("Desmarcando a un usuario...")
                        ActionChains(self.driver).move_to_element(item).click().perform()
                        time.sleep(0.5)
                        try:
                            username_element = item.find_element(By.XPATH, ".//span")
                            username = username_element.text.strip()

                            from utils import is_user_in_any_close_friends_list
                            found_lists = is_user_in_any_close_friends_list(username)

                            if not found_lists:
                                print(f"🟡 El usuario '{username}' no estaba en ninguna lista.")
                                import os
                                from pathlib import Path
                                close_friends_dir = Path("custom/close_friends")
                                available_lists = [f.name for f in close_friends_dir.glob("*.json")]

                                if available_lists:
                                    print("¿Deseas añadirlo a alguna de estas listas?")
                                    for idx, fname in enumerate(available_lists, 1):
                                        print(f"{idx}. {fname}")

                                    selection = input("Elige el número de la lista o presiona Enter para omitir: ").strip()
                                    if selection.isdigit():
                                        idx = int(selection) - 1
                                        if 0 <= idx < len(available_lists):
                                            chosen_file = close_friends_dir / available_lists[idx]
                                            try:
                                                import json
                                                with open(chosen_file, "r+", encoding="utf-8") as f:
                                                    data = json.load(f)
                                                    if not any(u.get("value") == username for u in data):
                                                        data.append({"value": username})
                                                        f.seek(0)
                                                        json.dump(data, f, indent=4)
                                                        f.truncate()
                                                        print(f"✅ Añadido a {available_lists[idx]}")
                                                    else:
                                                        print("ℹ️ Ya estaba en esa lista.")
                                            except Exception as e:
                                                print(f"❌ No se pudo escribir en {chosen_file}: {e}")
                                else:
                                    print("⚠️ No hay listas disponibles para añadir el usuario.")
                        except Exception as e:
                            print(f"⚠️ No se pudo obtener el nombre de usuario ni actualizar listas: {e}")
                    else:
                        print("Ya no hay más usuarios marcados. Finalizando.")
                        break

                except Exception as e:
                    print(f"Error al procesar un ítem: {e}")
                    continue

        except Exception as e:
            print(f"No se pudo cargar la lista de mejores amigos: {e}")

    def add_close_friends_from_file(self, json_path):
        """
        Agrega usuarios como mejores amigos desde un archivo JSON con formato: [{"value": "username"}]
        """
        import json

        print(f"Cargando usuarios desde '{json_path}'...")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception as e:
            print(f"❌ No se pudo leer el archivo: {e}")
            return

        self.driver.get("https://www.instagram.com/accounts/close_friends/")
        time.sleep(3)

        added = []
        skipped = []
        already_added = []

        for user in users:
            username = user.get("value", "").strip()
            if not username:
                continue

            try:
                input_box = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Buscar']"))
                )
                input_box.clear()
                input_box.send_keys(username)
                time.sleep(2.5)

                first_result = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='button' and contains(@style,'justify-content: space-between')]"))
                )

                username_span = first_result.find_element(By.XPATH, ".//span")
                found_username = username_span.text.strip()
                if found_username != username:
                    print(f"⚠️ Se encontró '{found_username}' en lugar de '{username}', saltando.")
                    skipped.append(username)
                    continue

                checkbox = first_result.find_element(By.XPATH, ".//div[contains(@style, 'background-color')]")
                is_checked = "rgb(0, 149, 246)" in checkbox.get_attribute("style")

                if is_checked:
                    print(f"✅ {username} ya estaba en mejores amigos.")
                    already_added.append(username)
                else:
                    print(f"➕ Añadiendo a {username}...")
                    first_result.click()
                    added.append(username)
                    time.sleep(1)

            except Exception as e:
                print(f"⚠️ Error al procesar '{username}': {e}")
                skipped.append(username)
                continue

        print(Fore.CYAN + "\nResumen del proceso de agregado a mejores amigos:")
        print(Fore.GREEN + f"✅ {len(added)} usuarios añadidos.")
        if already_added:
            print(Fore.YELLOW + f"🟡 {len(already_added)} ya estaban añadidos.")
        if skipped:
            print(Fore.RED + f"❌ {len(skipped)} no se pudieron añadir:")
            for name in skipped:
                print(Fore.RED + f"   - {name}")

    def close(self):
        """Cerrar el navegador"""
        self.driver.quit()