from typing import Optional
from src.models import Partenaire
from src.apps.interfaces.main_interfaces.partner_interface import PartenaireRepositoryInterface

class PartenaireRepository(PartenaireRepositoryInterface):
    def get_by_token(self, token: str) -> Optional[Partenaire]:
        try:
            return Partenaire.objects.get(token=token, is_active=True)
        except Partenaire.DoesNotExist:
            return None