# Punto de entrada de la aplicación

from data_loader import JsonLoader

def main():
    loader = JsonLoader()

    following = loader.load_following("data/following.json")
    followers = loader.load_followers("data/followers_1.json")

    # Obtener los usuarios que sigo pero no me siguen
    following_users = {user['value'] for user in following}
    followers_users = {user['value'] for user in followers}

    not_followed_back = following_users - followers_users  # Usuarios que sigo pero no me siguen

    # Mostrar cantidad y listado
    print(f"\nTotal de usuarios que sigues pero no te siguen: {len(not_followed_back)}")

    if len(not_followed_back) > 0:
        print("\n=== Usuarios que sigues pero no te siguen ===")
        for user in sorted(not_followed_back):
            print(f"- {user}")
    else:
        print("No hay usuarios que sigas pero que no te sigan.")

if __name__ == "__main__":
    main()