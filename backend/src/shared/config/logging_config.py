# logging_config.py - Configuration du logging partagé

import logging
import os
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_to_file: bool = True):
    """Configure le logging pour l'application"""

    # Créer le répertoire logs s'il n'existe pas
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configuration de base
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console
        ]
    )

    if log_to_file:
        # Handler pour les logs généraux
        file_handler = logging.FileHandler(logs_dir / "app.log")
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Ajouter le handler au logger root
        logging.getLogger().addHandler(file_handler)

        # Handler spécifique pour les erreurs
        error_handler = logging.FileHandler(logs_dir / "error.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        logging.getLogger().addHandler(error_handler)

def get_logger(name: str) -> logging.Logger:
    """Retourne un logger configuré"""
    return logging.getLogger(name)