# ACE Server Rules · Déployer la vidéo CSP

**Lecture obligatoire avant toute publication ou modification de la vidéo d’accueil.** Ce guide couvre le remplacement du MP4, l’activation sur un serveur et les vérifications en jeu.

## Choisir ce qui doit changer

| Besoin | Action | Effet côté serveur |
| --- | --- | --- |
| Changer la vidéo, sa qualité ou son volume | Remplacer [`ace-welcome-v1.mp4`](ace-welcome-v1.mp4) sur `main`, sous le même nom. | Aucun bloc à recopier. La nouvelle vidéo est utilisée à la prochaine connexion une fois l’URL publique actualisée. |
| Activer la vidéo sur un autre serveur ou changer le comportement du lecteur | Utiliser le bloc CSP ci-dessous. Si le Lua a changé, pointer vers la nouvelle révision validée. | Enregistrer dans les options CSP de l’événement qui sera lancé. |

Le lecteur [`ace_welcome.lua`](ace_welcome.lua) affiche la vidéo une fois par connexion, sur les serveurs où le bloc a été ajouté. Il lance le lecteur dans `script.update()` et dessine la fenêtre dans `script.drawUI()`. Le cadre 16:9 est réduit de 20 % dans chaque dimension par rapport au cadre d’origine. Un clic n’importe où ferme le panneau et coupe le son. La fin de la vidéo ferme aussi le panneau.

## Remplacer le MP4 à la même adresse

1. **Repartir du fichier source.** Exporter en MP4 avec vidéo H.264, pixels `yuv420p`, audio AAC et démarrage rapide (`-movflags +faststart`). Pour la vidéo ACE actuelle de 2 min 33 s, le profil publié est **1080p à 30 i/s**, environ **4,8 Mbit/s** pour la vidéo et **160 kbit/s** pour l’audio. Le MP4 final fait **95,5 Mo**.
2. **Vérifier la taille et le son.** Rester sous **100 Mio par fichier** pour garder l’adresse GitHub Raw. Viser environ 95 Mo pour cette durée. La piste actuelle intègre le gain sonore de **+15 %** (environ **+1,2 dB** mesuré par rapport à la première publication). Le lecteur reste à **50 %**. Si la piste change, mesurer le niveau du fichier final et limiter les crêtes au besoin.
3. **Publier via Git.** Le téléversement par navigateur est limité à **25 Mio**. Le connecteur GitHub a aussi refusé des fichiers que `git push` peut accepter. Utiliser un compte autorisé à publier dans ce dépôt et remplacer uniquement le MP4.

   Depuis un clone propre du dépôt, dans Git Bash ou un autre terminal compatible Bash. Avant le commit, la liste des fichiers préparés doit contenir uniquement `ace-welcome-v1.mp4`.

   ```bash
   git switch main
   git pull --ff-only
   cp "/chemin/vers/la-nouvelle-video.mp4" ace-welcome-v1.mp4
   git add -- ace-welcome-v1.mp4
   git diff --cached --name-only
   git commit -m "Update ACE CSP welcome video"
   git push origin main
   ```

4. **Vérifier ce que les joueurs recevront.** Télécharger le fichier depuis [l’URL exacte utilisée par le lecteur](https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/main/ace-welcome-v1.mp4). Comparer sa taille et son empreinte SHA-256 à l’export local. Si l’URL sert encore l’ancienne version, attendre l’actualisation du cache GitHub puis contrôler à nouveau.
5. **Vérifier en jeu à la prochaine connexion.** Contrôler l’image et le niveau sonore, puis le clic dans la vidéo et en dehors du cadre. Sur une autre connexion, laisser la lecture se terminer pour contrôler la fermeture automatique. Le décodage du MP4 et sa présence sur GitHub sont des contrôles distincts de la lecture dans CSP.

Pour un MP4 de plus de 100 Mio, une [GitHub Release](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas) est possible, avec une nouvelle URL vidéo à vérifier en jeu. Pour conserver l’URL actuelle, exporter un fichier sous la limite du dépôt. [Limites des fichiers GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github#file-size-limits)

## Activer la vidéo sur un serveur

Dans Assetto Corsa Server Manager, ouvrir **l’événement concerné → Custom Shaders Patch → Extra Options**. Ajouter le bloc suivant en conservant les autres réglages. Écrire **`[SCRIPT_...]`** avec les trois points. La révision ci-dessous a été vérifiée en jeu sur le League. Son URL est fixe et elle lit le MP4 de `main`.

```ini
[SCRIPT_...]
SCRIPT = 'https://raw.githubusercontent.com/assetto-corsa-elite/ace-server-rules/1443d8a2ade814b1fcf9f56ecde65d15275744c4/ace_welcome.lua'
REQUIRED = 1
```

Sur le League, ce bloc a fonctionné avec **Required Minimum CSP Version à `0`**. Conserver le réglage du serveur. Pour Road America, enregistrer la manche, puis lancer une **nouvelle** session depuis **Start Practice Event**. Le practice déjà en cours peut continuer à envoyer l’ancien lien après l’enregistrement. Le bouton **Restart** en haut du panneau peut relancer la configuration déjà chargée. Si une session tourne, obtenir l’accord de l’organisateur avant de l’arrêter. [Documentation des scripts CSP](https://github.com/ac-custom-shaders-patch/acc-extension-config/wiki/Misc-%E2%80%93-Server-extra-options#online-scripts)

Si le Lua change, publier la nouvelle révision, puis mettre à jour le bloc uniquement sur les serveurs choisis. Le fichier historique `ace_rules.lua` est distinct du lecteur vidéo actuel.

## Diagnostiquer un échec avant de modifier quoi que ce soit

Après une connexion, ouvrir `%USERPROFILE%\Documents\Assetto Corsa\logs\custom_shaders_patch.log`. Contrôler d’abord l’heure du dernier essai et l’URL sur la ligne `Remote server script`.

| Indice dans le journal | À vérifier |
| --- | --- |
| Aucune ligne `Remote server script` pour ACE | Vérifier l’événement actif, ses options CSP et le bloc enregistré. |
| `Remote server script` pointe vers une ancienne révision | Comparer au lien sauvegardé dans la manche. Si le panneau montre déjà la bonne révision, vérifier que le practice a été lancé à nouveau depuis cette manche. |
| `script loaded` sans `playback requested` | Vérifier la révision réellement chargée et le démarrage du lecteur dans `script.update()`. |
| `playback requested` sans `playback started` | Vérifier l’URL du MP4, sa disponibilité, son format et les erreurs de lecture. Le lecteur se ferme après 20 secondes sans progression. |
| `playback started` sans `overlay drawn` | Vérifier la fenêtre et le chemin d’affichage dans `script.drawUI()`. |
| `playback started` et `overlay drawn` | Vérifier visuellement la lecture, la netteté, le son et les deux modes de fermeture en jeu. |

Si un remplacement du MP4 pose problème, annuler le commit qui a remplacé le fichier avec `git revert`, pousser sur `main` et vérifier de nouveau l’URL publique. Le lien CSP reste identique.
