import json
from typing import List, Dict, Any

class JsonLoader:
    def __init__(self):
        # Almacenará la lista de seguidos y seguidores ya cargados
        self.following_data: List[Dict[str, Any]] = []
        self.followers_data: List[Dict[str, Any]] = []

    def load_following(self, path: str) -> List[Dict[str, Any]]:
        """Carga el archivo following.json y guarda internamente la lista de seguidos"""
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
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
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("El archivo de followers no es una lista")
            self.followers_data = [
                item["string_list_data"][0]
                for item in data
                if "string_list_data" in item and item["string_list_data"]
            ]
            return self.followers_data

    def get_following(self) -> List[Dict[str, Any]]:
        """Devuelve la lista de seguidos cargados"""
        return self.following_data

    def get_followers(self) -> List[Dict[str, Any]]:
        """Devuelve la lista de seguidores cargados"""
        return self.followers_data