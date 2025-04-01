from data_loader import JsonLoader
from scraper import InstagramScraper

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
        print("1 - Usuarios que te siguen pero no sigues")
        print("2 - Solicitudes pendientes")
        print("3 - Usuarios que sigues pero no te siguen")
        print("4 - Verificar estado del botón de seguimiento")
        print("5 - Salir")

        choice = input("Elige una opción (1, 2, 3, 4, 5): ")

        if choice == '1':
            # Usuarios que te siguen pero no sigues
            followers_users = {user['value'] for user in followers}
            following_users = {user['value'] for user in following}

            not_followed_back = followers_users - following_users  # Seguidores que no sigues

            print(f"\nTotal de usuarios que te siguen pero no sigues: {len(not_followed_back)}")
            if len(not_followed_back) > 0:
                paginate(sorted(not_followed_back))
            else:
                print("No hay usuarios que te sigan pero que no sigas.")

        elif choice == '2':
            # Solicitudes pendientes
            pending_users = sorted({user['value'] for user in pending_requests})
            print(f"\nTotal de solicitudes pendientes: {len(pending_users)}")

            if len(pending_users) > 0:
                page_size = 30
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
                        for user in page_data:
                            if scraper.unfollow_if_requested(user):
                                cancelled_count += 1

                        print(f"\n{cancelled_count} de {len(page_data)} solicitudes canceladas.")

                    next_action = input("\nPresiona Enter para ver la siguiente página o 'q' para volver al menú principal: ")
                    if next_action.lower() == 'q':
                        break

                    current_page += 1
            else:
                print("No tienes solicitudes pendientes.")

        elif choice == '3':
            # Usuarios que sigues pero no te siguen
            following_users = {user['value'] for user in following}
            followers_users = {user['value'] for user in followers}

            not_followed_by = following_users - followers_users  # Los que sigues pero no te siguen

            print(f"\nTotal de usuarios que sigues pero no te siguen: {len(not_followed_by)}")
            if len(not_followed_by) > 0:
                paginate(sorted(not_followed_by))
            else:
                print("No sigues a nadie que no te siga.")

        elif choice == '4':
            profile_url = input("Ingresa la URL del perfil: ")
            status = scraper.check_follow_button(profile_url)

            if status:
                print(f"El estado del botón es: {status}")
            else:
                print("No se pudo determinar el estado de seguimiento.")
                
        else:
             # Salir
            scraper.close()
            print("Saliendo de la aplicación...")
            break

if __name__ == "__main__":
    main()