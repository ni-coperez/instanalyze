import json
from typing import List, Dict, Any

class JsonLoader:
    def __init__(self):
        # Almacenará la lista de seguidos, seguidores y solicitudes pendientes ya cargados
        self.following_data: List[Dict[str, Any]] = []
        self.followers_data: List[Dict[str, Any]] = []
        self.pending_requests_data: List[Dict[str, Any]] = []

    def load_json(self, path: str) -> Dict[str, Any]:
        """Carga un archivo JSON y maneja posibles errores"""
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise ValueError(f"Error al cargar el archivo {path}: {e}")

    def load_following(self, path: str) -> List[Dict[str, Any]]:
        """Carga el archivo following.json y guarda internamente la lista de seguidos"""
        data = self.load_json(path)
        if "relationships_following" not in data:
            raise ValueError("El archivo no tiene la clave 'relationships_following'")
        self.following_data = [
            item["string_list_data"][0]
            for item in data["relationships_following"]
            if "string_list_data" in item and item["string_list_data"]
        ]
        return self.following_data

    def load_followers(self, path: str) -> List[Dict[str, Any]]:
        """Carga el archivo followers_1.json y guarda internamente la lista de seguidores"""
        data = self.load_json(path)
        if not isinstance(data, list):
            raise ValueError("El archivo de followers no es una lista")
        self.followers_data = [
            item["string_list_data"][0]
            for item in data
            if "string_list_data" in item and item["string_list_data"]
        ]
        return self.followers_data

    def load_pending_follow_requests(self, path: str) -> List[Dict[str, Any]]:
        """Carga el archivo pending_follow_requests.json y guarda internamente las solicitudes pendientes"""
        data = self.load_json(path)
        if "relationships_follow_requests_sent" not in data:
            raise ValueError("El archivo no tiene la clave 'relationships_follow_requests_sent'")
        self.pending_requests_data = [
            item["string_list_data"][0]
            for item in data["relationships_follow_requests_sent"]
            if "string_list_data" in item and item["string_list_data"]
        ]
        return self.pending_requests_data

    def save_pending_follow_requests(self, path: str, pending_requests: List[Dict[str, Any]]) -> None:
        """Guarda la lista de solicitudes pendientes en un archivo JSON"""
        data = {"relationships_follow_requests_sent": [{"string_list_data": [item]} for item in pending_requests]}
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Error al guardar el archivo {path}: {e}")

    def save_following(self, path: str, following_data: List[Dict[str, Any]]) -> None:
        """Guarda la lista de seguidos en un archivo JSON"""
        data = {
            "relationships_following": [
                {"string_list_data": [item], "media_list_data": [], "title": ""}
                for item in following_data
            ]
        }
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Error al guardar el archivo {path}: {e}")

    def get_following(self) -> List[Dict[str, Any]]:
        """Devuelve la lista de seguidos cargados"""
        return self.following_data

    def get_followers(self) -> List[Dict[str, Any]]:
        """Devuelve la lista de seguidores cargados"""
        return self.followers_data

    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Devuelve la lista de solicitudes de seguimiento pendientes cargadas"""
        return self.pending_requests_data