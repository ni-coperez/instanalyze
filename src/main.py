import time
from data_loader import JsonLoader
from scraper import InstagramScraper
import json
from colorama import init, Fore, Style
from pyfiglet import Figlet
import pwinput

init(autoreset=True)  # Inicializar colorama

def paginate(data, page_size=30):
    """Función para paginar los resultados"""
    total_pages = (len(data) + page_size - 1) // page_size  # Calcular el número de páginas
    current_page = 1
    while True:
        start = (current_page - 1) * page_size
        end = start + page_size
        page_data = data[start:end]

        print(Fore.YELLOW + "\n----------------------------------------")
        print(Fore.CYAN + f"Página {current_page} de {total // page_size + (total % page_size > 0)}")
        print(Fore.CYAN + f"¿Deseas dejar de seguir a los {len(page_data)} usuarios en esta página?")
        print(Fore.YELLOW + "----------------------------------------")

        action = input(Fore.WHITE + "(s = sí / n = no): ").strip().lower()

        if action == 's':
            cancelled_count = 0
            users_to_remove = []  # Lista de usuarios a eliminar

            for user in page_data:
                print(Fore.YELLOW + "\n----------------------------------------")
                print(Fore.RED + f"Cancelación de solicitud para: {user}")
                print(Fore.YELLOW + "----------------------------------------")

                if scraper.unfollow_if_requested(user):
                    print(Fore.GREEN + f"✔ Cancelación confirmada para: {user}")
                    cancelled_count += 1
                    users_to_remove.append(user)  # Marcar usuario para eliminar

            # Eliminar del JSON los usuarios que se dejaron de seguir
            pending_requests = [req for req in pending_requests if req['value'] not in users_to_remove]

            # Guardar cambios en el archivo JSON
            loader.save_pending_follow_requests("data/pending_follow_requests.json", pending_requests)

            print(Fore.YELLOW + "\n----------------------------------------")
            print(Fore.GREEN + f"{cancelled_count} de {len(page_data)} solicitudes canceladas.")
            print(Fore.YELLOW + "----------------------------------------\n")

        next_action = input("\nPresiona Enter para ver la siguiente página o 'q' para volver al menú principal: ")
        if next_action.lower() == 'q':
            break

        current_page += 1

def mostrar_menu():
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('Instanalyze'))
    print(Style.BRIGHT + Fore.CYAN + "================== MENÚ ==================")
    print(Fore.YELLOW + "1." + Fore.WHITE + " Eliminar solicitudes pendientes")
    print(Fore.YELLOW + "2." + Fore.WHITE + " Eliminar usuarios que sigues pero no te siguen")
    print(Fore.YELLOW + "3." + Fore.WHITE + " Salir")
    print(Fore.CYAN + "==========================================")
    
def main():
    loader = JsonLoader()

    following = loader.load_following("data/following.json")
    followers = loader.load_followers("data/followers_1.json")
    pending_requests = loader.load_pending_follow_requests("data/pending_follow_requests.json")

    print(Fore.YELLOW + "\n----------------------------------------")
    print(Fore.CYAN + "Inicio de sesión en Instagram")
    print(Fore.YELLOW + "----------------------------------------")

    username = input(Fore.WHITE + "👤 Usuario: ").strip()
    password = pwinput.pwinput(prompt=Fore.WHITE + "🔒 Contraseña: ", mask="*")

    scraper = InstagramScraper(username, password)
    scraper.login()

    while True:
        mostrar_menu()
        choice = input(Fore.GREEN + "Elige una opción (1-3): " + Style.RESET_ALL).strip()

        if choice == '1':
                # Solicitudes pendientes
                pending_users = sorted({user['value'] for user in pending_requests})
                total = len(pending_users)
                print(Fore.YELLOW + "\n----------------------------------------")
                print(Fore.CYAN + f"Total de solicitudes pendientes: {total}")
                print(Fore.YELLOW + "----------------------------------------\n")

                if total > 0:
                    try:
                        page_input = input(Fore.WHITE + "¿Cuántos perfiles deseas ver por página? (Enter para usar 500): ").strip()
                        page_size = int(page_input) if page_input else 500
                        if page_size > total:
                            print(Fore.YELLOW + f"⚠️ El tamaño excede el total de usuarios. Se usará {total}.")
                            page_size = total
                    except ValueError:
                        print(Fore.RED + "❌ Valor inválido. Se usará el tamaño por defecto de 500.")
                        page_size = min(500, total)

                    current_page = 1

                    while current_page <= total // page_size + (total % page_size > 0):
                        start = (current_page - 1) * page_size
                        end = start + page_size
                        page_data = pending_users[start:end]

                        print(Fore.YELLOW + "\n----------------------------------------")
                        print(Fore.CYAN + f"Página {current_page} de {total // page_size + (total % page_size > 0)}")
                        print(Fore.CYAN + f"¿Deseas dejar de seguir a los {len(page_data)} usuarios en esta página?")
                        print(Fore.YELLOW + "----------------------------------------")

                        action = input(Fore.WHITE + "(s = sí / n = no): ").strip().lower()

                        if action == 's':
                            cancelled_count = 0
                            users_to_remove = []  # Lista de usuarios a eliminar

                            for user in page_data:
                                print(Fore.YELLOW + "\n----------------------------------------")
                                print(Fore.RED + f"Cancelación de solicitud para: {user}")
                                print(Fore.YELLOW + "----------------------------------------")

                                if scraper.unfollow_if_requested(user):
                                    print(Fore.GREEN + f"✔ Cancelación confirmada para: {user}")
                                    cancelled_count += 1
                                    users_to_remove.append(user)  # Marcar usuario para eliminar

                            # Eliminar del JSON los usuarios que se dejaron de seguir
                            pending_requests = [req for req in pending_requests if req['value'] not in users_to_remove]

                            # Guardar cambios en el archivo JSON
                            loader.save_pending_follow_requests("data/pending_follow_requests.json", pending_requests)

                            print(Fore.YELLOW + "\n----------------------------------------")
                            print(Fore.GREEN + f"{cancelled_count} de {len(page_data)} solicitudes canceladas.")
                            print(Fore.YELLOW + "----------------------------------------\n")

                        next_action = input("\nPresiona Enter para ver la siguiente página o 'q' para volver al menú principal: ")
                        if next_action.lower() == 'q':
                            break

                        current_page += 1
                else:
                    print("No tienes solicitudes pendientes.")

        elif choice == '2':
            # Usuarios que sigues pero no te siguen
            following_users = {user['value'] for user in following}
            followers_users = {user['value'] for user in followers}

            not_followed_by = sorted(following_users - followers_users)

            # Cargar white list
            try:
                with open("data/white_list.json", "r", encoding="utf-8") as f:
                    white_list = {entry['value'] for entry in json.load(f)}
            except (FileNotFoundError, json.JSONDecodeError):
                white_list = set()

            # Filtrar usuarios que no están en la whitelist
            filtered_users = [user for user in not_followed_by if user not in white_list]

            print(f"\nTotal de usuarios que sigues pero no te siguen (filtrados): {len(filtered_users)}")

            for user in filtered_users:
                print(Fore.YELLOW + "\n----------------------------------------")
                print(Fore.RED + f"Cancelación de solicitud para: {user}")
                print(Fore.YELLOW + "----------------------------------------")

                scraper.view_profile(user)
                
                action = input("¿Dejar de seguir (d) / Agregar a whitelist (w) / Saltar (s) / Salir (q)? ").strip().lower()

                if action == 'q':
                    print("Saliendo del recorrido de usuarios.")
                    break
                elif action == 'w':
                    print(f"Añadiendo {user} a la white list...")
                    white_list.add(user)
                elif action == 'd':
                    if scraper.unfollow_if_requested(user):
                        print(Fore.GREEN + f"✔ Cancelación confirmada para: {user}")
                        following = [u for u in following if u['value'] != user]
                else:
                    print("Saltando...")

            # Guardar archivo de following actualizado
            loader.save_following("data/following.json", following)

            # Guardar white list actualizada
            with open("data/white_list.json", "w", encoding="utf-8") as f:
                json.dump([{"value": user} for user in sorted(white_list)], f, indent=4, ensure_ascii=False)

        else:
            # Salir
            scraper.close()
            print(Fore.MAGENTA + "¡Hasta la próxima!")
            break

if __name__ == "__main__":
    main()