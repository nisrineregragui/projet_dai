"""Authentification par clé API, transmise dans l'en-tête X-API-Key."""
import secrets

from fastapi import Header, HTTPException, status

from maintai.config import get_settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Refuse la requête si la clé est absente ou fausse."""
    # TODO (TP2) : Comparez x_api_key à get_settings().api_key avec secrets.compare_digest : 401 si la clé est absente ou fausse, 500 si le serveur n'a pas de clé configurée
    if not get_settings().api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée côté serveur",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, get_settings().api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante",
        )

