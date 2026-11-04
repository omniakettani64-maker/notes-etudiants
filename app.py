
# ============================================================
# Application de consultation et de modification des notes
# ============================================================

import os
import math
import sqlite3

from flask import Flask, jsonify, request
from auth import utilisateur_connecte

app = Flask(__name__)

# Fichier où sont conservées les notes
DB = "notes.db"


# Préparation de la base de données
def init_db():
    with sqlite3.connect(DB) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                etudiant TEXT,
                module TEXT,
                note REAL
            )
            """
        )

        if con.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 0:
            con.executemany(
                """
                INSERT INTO notes (etudiant, module, note)
                VALUES (?, ?, ?)
                """,
                [
                    ("Amina", "DevSecOps", 15.5),
                    ("Youssef", "DevSecOps", 12.0)
                ],
            )


init_db()


# Page d'accueil
@app.route("/")
def accueil():
    return (
        "<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'>"
        "<title>Notes des etudiants</title></head><body>"
        "<h1>Consultation des notes</h1>"
        "<p><a href='/notes'>Voir les notes</a></p></body></html>"
    )


# Vérification de disponibilité du service
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": "1.0"
    })


# Consultation et recherche des notes
@app.route("/notes")
def lister_notes():
    etudiant = request.args.get("etudiant", "")

    with sqlite3.connect(DB) as con:
        rows = con.execute(
            """
            SELECT id, etudiant, module, note
            FROM notes
            WHERE etudiant LIKE ?
            """,
            (f"%{etudiant}%",),
        ).fetchall()

    return jsonify([
        {
            "id": r[0],
            "etudiant": r[1],
            "module": r[2],
            "note": r[3]
        }
        for r in rows
    ])


# ============================================================
# Modification sécurisée d'une note par un enseignant
# ============================================================

@app.route("/notes/<int:note_id>", methods=["PUT"])
def modifier_note(note_id):

    # S2 : authentification obligatoire
    utilisateur = utilisateur_connecte()

    if utilisateur is None:
        return jsonify({"erreur": "Authentification requise"}), 401

    # S3 : seul un enseignant peut modifier une note
    if utilisateur.get("role") != "enseignant":
        return jsonify({"erreur": "Accès interdit"}), 403

    # Récupération et validation des données
    donnees = request.get_json(silent=True)

    if not isinstance(donnees, dict):
        return jsonify({"erreur": "Données invalides"}), 400

    nouvelle_note = donnees.get("note")

    # S5 : validation de la note
    if (
        isinstance(nouvelle_note, bool)
        or not isinstance(nouvelle_note, (int, float))
        or not math.isfinite(nouvelle_note)
        or not 0 <= nouvelle_note <= 20
    ):
        return jsonify({"erreur": "La note doit être comprise entre 0 et 20"}), 400

    try:
        with sqlite3.connect(DB) as con:

            # Vérifier que la note existe et récupérer son module
            resultat = con.execute(
                "SELECT module FROM notes WHERE id = ?",
                (note_id,)
            ).fetchone()

            if resultat is None:
                return jsonify({"erreur": "Note introuvable"}), 404

            module_note = resultat[0]

            # S4 : vérifier que l'enseignant appartient au bon module
            if utilisateur.get("module") != module_note:
                return jsonify({"erreur": "Modification non autorisée"}), 403

            # S6 : modification sécurisée avec requête paramétrée
            con.execute(
                "UPDATE notes SET note = ? WHERE id = ?",
                (nouvelle_note, note_id)
            )

        return jsonify({
            "message": "Note modifiée avec succès",
            "note": nouvelle_note
        }), 200

    except sqlite3.Error:
        # S7 : ne pas divulguer les détails techniques
        app.logger.exception("Erreur interne lors de la modification")
        return jsonify({"erreur": "Une erreur interne est survenue"}), 500


# Démarrage du service
if __name__ == "__main__":
    app.run(
        host=os.environ.get("APP_HOST", "127.0.0.1"),
        port=5000
    )
