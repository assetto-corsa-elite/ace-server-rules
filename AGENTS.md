# Vidéo d’accueil ACE

Avant toute tâche liée à la vidéo d’accueil CSP, lire intégralement le [guide de déploiement](README.md) à la racine du dépôt.

- Pour remplacer uniquement la vidéo, conserver le chemin public `main/ace-welcome-v1.mp4` et le bloc CSP en place.
- En cas de panne, identifier la révision réellement chargée dans le journal CSP avant de modifier le Lua ou la configuration d’un serveur.
- Vérifier l’URL publique après publication. Indiquer séparément si la lecture a été vérifiée en jeu.

## Championship Manager: required integration reading

Before any CM/Post Results integration work, read [VSC_INTEGRATION.md](Championship%20Manager/VSC_INTEGRATION.md) in full, then its required supporting contracts. It defines producer vs implementer responsibilities, the native Post Results sidebar section, championship tabs, channel configuration, sanctions/cancellation, histories and shared Discord/CM permissions. Do not implement from an isolated chat summary.

If working in a separate CM application repository, add this canonical guide link to that repository's existing AGENTS.md or equivalent VSC instructions so it is discovered there too. Preserve existing application instructions. The content repository does not contain the CM runtime.

Before implementing or changing sanctions, read [ACSM-Penalties-POST.md](Championship%20Manager/ACSM-Penalties-POST.md) in full. It specifies the verified HTTP forms, cancellation rules, and scheduled Blocklist execution for authorized round and league bans.

## Automatic Post Results: mandatory editorial reading

Before producing any league post or poster, including a manual chat delivery, read [EDITORIAL.md](Championship%20Manager/EDITORIAL.md) and [PRODUCTION.md](Championship%20Manager/PRODUCTION.md) in full. Follow their visual composition and acceptance requirements: information-bearing visuals by default, necessary complete table exceptions, private per-poster inspection evidence, canonical publication nomenclature and owner corrections applied in place. Do not copy post text into list-based posters or narrate internal alias corrections.
