from typing import Optional, List
from abc import ABC, abstractmethod

class UserRepositoryInterface(ABC):
    """Interface pour le repository utilisateur"""

    @abstractmethod
    def get_by_id(self, user_id: int):
        pass

    @abstractmethod
    def get_by_email(self, email: str):
        pass

    @abstractmethod
    def get_by_nin(self, nin: str):
        pass

    @abstractmethod
    def save(self, user):
        pass

    @abstractmethod
    def delete(self, user):
        pass

    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        pass

    @abstractmethod
    def exists_by_nin(self, nin: str) -> bool:
        pass

    @abstractmethod
    def get_active_users(self) -> list:
        pass

    @abstractmethod
    def update_last_login(self, user) -> None:
        pass