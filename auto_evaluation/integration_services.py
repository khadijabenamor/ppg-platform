"""
Service d'intégration pour le Module M3 (Auto-évaluation)
Ce service permet de récupérer les contenus des cours du Module M1 (Ressources Pédagogiques)
"""
from typing import Optional, List, Dict, Any
import requests


class CourseIntegrationService:
    """
    Service pour récupérer les contenus des cours depuis le Module M1.
    À utiliser pour générer des questions et flashcards automatiquement.
    """
    
    def __init__(self, m1_base_url: str = "http://127.0.0.1:8000"):
        self.m1_base_url = m1_base_url
        self.resources_endpoint = f"{m1_base_url}/api/resources/"
        self.courses_endpoint = f"{m1_base_url}/api/courses/"
    
    def get_course_content(self, course_id: str) -> Optional[str]:
        """
        Récupère le contenu textuel d'un cours.
        
        Args:
            course_id: ID du cours
            
        Returns:
            Contenu textuel du cours ou None si non trouvé
        """
        try:
            response = requests.get(f"{self.courses_endpoint}{course_id}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
            return None
        except requests.RequestException:
            return None
    
    def get_course_resources(self, course_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les ressources d'un cours.
        
        Args:
            course_id: ID du cours
            
        Returns:
            Liste des ressources (PDFs, images, etc.)
        """
        try:
            response = requests.get(f"{self.resources_endpoint}?course_id={course_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except requests.RequestException:
            return []
    
    def extract_text_from_resources(self, resources: List[Dict]) -> str:
        """
        Extrait le texte de toutes les ressources.
        
        Args:
            resources: Liste des ressources
            
        Returns:
            Texte concaténé de toutes les ressources
        """
        texts = []
        for resource in resources:
            if resource.get("type") == "pdf":
                # Pour les PDFs, utiliser l'OCR ou l'extraction
                text = resource.get("extracted_text", "")
                if text:
                    texts.append(text)
            elif resource.get("type") == "text":
                texts.append(resource.get("content", ""))
        
        return "\n\n".join(texts)
    
    def get_full_course_content(self, course_id: str) -> Dict[str, Any]:
        """
        Récupère le contenu complet d'un cours (description + ressources).
        
        Args:
            course_id: ID du cours
            
        Returns:
            Dict contenant 'description' et 'content'
        """
        try:
            # Récupérer les infos du cours
            course_response = requests.get(f"{self.courses_endpoint}{course_id}/", timeout=10)
            
            if course_response.status_code != 200:
                return {"description": "", "content": "", "resources": []}
            
            course_data = course_response.json()
            
            # Récupérer les ressources
            resources = self.get_course_resources(course_id)
            content = self.extract_text_from_resources(resources)
            
            return {
                "description": course_data.get("description", ""),
                "content": content,
                "resources": resources,
                "title": course_data.get("title", "")
            }
        except requests.RequestException:
            return {"description": "", "content": "", "resources": []}


class UserIntegrationService:
    """
    Service pour gérer l'intégration avec le module d'authentification (M4).
    """
    
    def __init__(self, auth_base_url: str = "http://127.0.0.1:8000"):
        self.auth_base_url = auth_base_url
        self.users_endpoint = f"{auth_base_url}/api/auth/users/"
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """
        Récupère le profil d'un utilisateur depuis le module M4.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Données du profil utilisateur
        """
        try:
            response = requests.get(f"{self.users_endpoint}{user_id}/", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    def check_user_subscription(self, user_id: int) -> str:
        """
        Vérifie le type d'abonnement de l'utilisateur (Free/Premium).
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            'free' ou 'premium'
        """
        try:
            response = requests.get(f"{self.users_endpoint}{user_id}/subscription/", timeout=10)
            if response.status_code == 200:
                return response.json().get("type", "free")
            return "free"
        except requests.RequestException:
            return "free"


# Instance globale du service (pour utilisation dans les use cases)
course_integration_service = CourseIntegrationService()
user_integration_service = UserIntegrationService()