
# ============================================================
# Identification des utilisateurs de l'application des notes
# ============================================================

import json
import os

from flask import request

# Les jetons sont conservés dans un fichier externe
FICHIER_JETONS = os.environ.get("FICHIER_JETONS", "jetons.json")


# Retrouve l'utilisateur à partir du jeton
def utilisateur_connecte():
    entete = request.headers.get("Authorization", "")

    if not entete.startswith("Bearer "):
        return None

    try:
        with open(FICHIER_JETONS, encoding="utf-8") as fichier:
            jetons = json.load(fichier)

    except (FileNotFoundError, json.JSONDecodeError):
        return None

    return jetons.get(entete.removeprefix("Bearer "))
