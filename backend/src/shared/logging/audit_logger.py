# audit_logger.py - Logging partagé pour l'audit

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

class AuditLogger:
    """Logger spécialisé pour l'audit système"""

    def __init__(self, name: str = "audit"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Créer un handler pour l'audit si pas déjà présent
        if not any(isinstance(h, logging.FileHandler) and 'audit' in h.baseFilename for h in self.logger.handlers):
            handler = logging.FileHandler('logs/audit.log')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)

    def log_action(self, action: str, user_id: Optional[str] = None,
                   resource: Optional[str] = None, details: Optional[Dict[str, Any]] = None,
                   ip_address: Optional[str] = None):
        """Log une action d'audit"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address
        }

        self.logger.info(json.dumps(log_entry))

    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """Log un événement de sécurité"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }

        if severity.upper() == "HIGH":
            self.logger.error(json.dumps(log_entry))
        elif severity.upper() == "MEDIUM":
            self.logger.warning(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))