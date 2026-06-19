# Pourquoi separer access_token et refresh_token ?

## La question

Pourquoi utiliser deux tokens de durees differentes (access_token court,
refresh_token long) plutot qu'un seul token a longue duree de vie ?

## Analyse par scenario de vol

### Scenario 1 : vol de l'access_token

L'access_token est envoye a chaque requete HTTP et est donc expose plus
frequemment (logs, proxies, historique reseau). Si un attaquant le vole :

- Il peut usurper l'identite de l'utilisateur, **mais seulement pendant 15 minutes**.
- Apres expiration, le token est automatiquement invalide.
- L'attaquant ne peut pas generer un nouveau token car il n'a pas le refresh_token.

Le dommage est **limite dans le temps** par la courte duree de vie.

### Scenario 2 : vol du refresh_token

Le refresh_token est envoye beaucoup moins souvent (uniquement pour se renouveler)
et est en general stocke de maniere plus securisee (cookie HttpOnly, secure storage).
Si un attaquant le vole :

- Il peut generer de nouveaux access_tokens indefiniment (7 jours).
- C'est un risque majeur, mais le refresh_token peut etre **revoque en base** car
  le serveur le stocke, contrairement aux JWT d'access.

La revocation est **possible et precise** : on supprime uniquement le refresh_token
compromis sans impacter les autres sessions.

## Conclusion

Un seul token a longue duree de vie cumule les deux risques : expose comme un
access_token, invalide difficile comme un refresh_token sans blacklist coteuse.
La separation permet d'appliquer le principe de **moindre privilege** :
exposer frequemment ce qui expire vite, et proteger ce qui dure longtemps.
