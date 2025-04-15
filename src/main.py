import time
from data_loader import JsonLoader
from scraper import InstagramScraper
import json

def paginate(data, page_size=30):
    """Función para paginar los resultados"""
    total_pages = (len(data) + page_size - 1) // page_size  # Calcular el número de páginas
    current_page = 1
    while True:
        start = (current_page - 1) * page_size
        end = start + page_size
        page_data = data[start:end]

        print(f"\nPágina {current_page} de {total_pages}")
        for item in page_data:
            print(f"- {item}")
        
        if current_page < total_pages:
            next_action = input("\nPresiona Enter para ver la siguiente página o 'q' para salir: ")
            if next_action.lower() == 'q':
                break
            current_page += 1
        else:
            break

def main():
    loader = JsonLoader()

    following = loader.load_following("data/following.json")
    followers = loader.load_followers("data/followers_1.json")
    pending_requests = loader.load_pending_follow_requests("data/pending_follow_requests.json")

    username = input("Ingresa tu usuario de Instagram: ")
    password = input("Ingresa tu contraseña: ")

    scraper = InstagramScraper(username, password)
    scraper.login()

    while True:
        print("\nSeleccione una opción:")
        print("1 - Eliminar las Solicitudes pendientes")
        print("2 - Eliminar Usuarios que sigues pero no te siguen")
        print("3 - Salir")

        choice = input("Elige una opción (1, 2, 3): ")

        if choice == '1':
                # Solicitudes pendientes
                pending_users = sorted({user['value'] for user in pending_requests})
                print(f"\nTotal de solicitudes pendientes: {len(pending_users)}")

                if len(pending_users) > 0:
                    page_size = 500
                    total_pages = (len(pending_users) + page_size - 1) // page_size
                    current_page = 1

                    while current_page <= total_pages:
                        start = (current_page - 1) * page_size
                        end = start + page_size
                        page_data = pending_users[start:end]

                        print(f"\nPágina {current_page} de {total_pages}")
                        for item in page_data:
                            print(f"- {item}")

                        action = input("\n¿Deseas dejar de seguir a estos contactos? (s/n): ").strip().lower()
                        if action == 's':
                            cancelled_count = 0
                            users_to_remove = []  # Lista de usuarios a eliminar

                            for user in page_data:
                                if scraper.unfollow_if_requested(user):
                                    cancelled_count += 1
                                    users_to_remove.append(user)  # Marcar usuario para eliminar

                            # Eliminar del JSON los usuarios que se dejaron de seguir
                            pending_requests = [req for req in pending_requests if req['value'] not in users_to_remove]

                            # Guardar cambios en el archivo JSON
                            loader.save_pending_follow_requests("data/pending_follow_requests.json", pending_requests)

                            print(f"\n{cancelled_count} de {len(page_data)} solicitudes canceladas.")

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
                print(f"\nPerfil: {user}")
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
                        print(f"Eliminando {user} del JSON de following.")
                        following = [u for u in following if u['value'] != user]
                else:
                    print("Saltando...")

            # Guardar archivo de following actualizado
            loader.save_following("data/following.json", following)

            # Guardar white list actualizada
            with open("data/white_list.json", "w", encoding="utf-8") as f:
                json.dump([{"value": user} for user in sorted(white_list)], f, indent=4, ensure_ascii=False)

        elif choice == '3':
            # Salir
            scraper.close()
            print("Saliendo de la aplicación...")
            break

if __name__ == "__main__":
    main()