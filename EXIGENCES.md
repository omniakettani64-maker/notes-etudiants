
# Exigences de sécurité de l'application des notes

| # | Exigence : « Le système doit… » | Vérification | Étape du SDLC | Test |
|---|---|---|---|---|
| 1 | empêcher les injections SQL lors de la recherche d'un étudiant. | Une recherche malveillante ne doit pas retourner tous les étudiants. | Développement et tests | S1 |
| 2 | exiger une authentification par jeton pour modifier une note. | Sans jeton valide, l'API retourne HTTP 401. | Développement et tests | S2 |
| 3 | réserver la modification des notes aux enseignants. | Un étudiant reçoit HTTP 403. | Développement et tests | S3 |
| 4 | autoriser un enseignant à modifier uniquement les notes de son module. | Un enseignant d'un autre module reçoit HTTP 403. | Développement et tests | S4 |
| 5 | accepter uniquement une note numérique comprise entre 0 et 20. | Une note invalide entraîne HTTP 400. | Développement et tests | S5 |
| 6 | permettre à un enseignant autorisé de modifier une note. | La modification réussie retourne HTTP 200 et la nouvelle note est enregistrée. | Développement et tests | S6 |
| 7 | ne jamais exposer les détails techniques des erreurs à l'utilisateur. | La réponse ne contient pas de détails internes sur la base de données. | Tests et maintenance | S7 |
