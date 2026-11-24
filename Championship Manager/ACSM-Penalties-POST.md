# ACE — Intégrer les sanctions ACSM dans Championship Manager

Le backend du bot exécute les opérations HTTP authentifiées. Le panneau Post Results affiche le résultat vérifié, l’historique, les erreurs et l’action Annuler par sanction. Réutiliser le client HTTP et le workflow Blocklist existants pour chaque serveur.

## Points au classement

Navigation : championnat → Driver Standings → ligne du pilote → Penalties → Set Penalty.

Le formulaire ACSM envoie :

    POST /championship/{championshipId}/driver-penalty/{standingsKey}/{guid}
    Content-Type: application/x-www-form-urlencoded

    PointsPenalty=7&action=set

Résoudre l’action du formulaire de la ligne du pilote et conserver le segment intermédiaire comme identifiant opaque. Le nom affiché sert à la présentation. Conserver le GUID sous forme de chaîne. Les noms de champs sont sensibles à la casse.

Lire le total de pénalité courant dans Points Penalty. Ajouter 2 à 5 implique d’envoyer 7. Annuler ces 2 sur un total courant de 7 implique d’envoyer 5. Avec un total courant de 2, envoyer 0. Si une sanction ultérieure a porté le total à 10, annuler la première de 2 implique d’envoyer 8. Le score affiché au championnat est diminué par ce total.

## Secondes au résultat de course

Navigation : championnat → Overview → View Results du round → Race → ligne du pilote → Penalties.

    POST /penalties/{resultKey}/{guid}?model={carModel}&event-id={eventId}&session-index={sessionIndex}
    Content-Type: application/x-www-form-urlencoded

    time-penalty=5&action=add

Lire l’URL d’action exacte du formulaire du résultat. Garder la clé du résultat, le modèle de voiture, l’identifiant de l’event et l’index de session fournis par ACSM. Toujours sélectionner la session Race. Encoder les valeurs via le client HTTP et conserver les paramètres de l’action. L’interface expose un pas de 0,001 seconde. Calculer en millisecondes entières dans le bot et sérialiser en secondes avec un point décimal.

**Add Penalty remplace le total pour cette ligne.** Le test a montré 2 secondes, puis 3 secondes après un envoi de 3. Pour cumuler +3 sur 2, envoyer 5. Lire le total appliqué dans le résultat affiché, car le champ de saisie peut être vide malgré une sanction active.

- Annulation avec d’autres secondes restant dues : envoyer le nouveau total positif via action=add.
- Annulation de la dernière sanction : même URL, corps time-penalty=&action=remove, équivalent au bouton Remove Penalty avec le champ vide.
- ACSM affiche que 0 via Add Penalty disqualifie le pilote. Traiter une disqualification existante comme un état distinct et signaler un conflit si une opération sur les secondes l’écraserait.

## Exécution HTTP et reprise

1. Lire la page avec la session du serveur ACSM. Résoudre le formulaire et relire l’état courant. La session admin, le serveur et les identifiants du résultat ou du classement doivent correspondre à la sanction.
2. Sérialiser les opérations par cible dans la base du bot. Enregistrer un ID d’opération unique, l’auteur, le motif, le delta, le total lu, le total cible et les identifiants ACSM avant l’écriture. Une annulation référence l’ID de la sanction et s’exécute une seule fois.
3. Envoyer le formulaire authentifié, avec les champs cachés requis s’ils sont présents et le bouton choisi via son champ action. Réutiliser la connexion. Relire l’état ACSM après réponse ou timeout. Un statut HTTP positif ou une redirection seuls ne prouvent pas l’application. Traiter la page de login comme une expiration de session.
4. En reprise, si l’état correspond à la cible persistée, clôturer l’opération. S’il correspond encore à l’état de départ, rejouer la même écriture absolue. Si une troisième valeur apparaît, exposer un conflit et préserver la modification externe. Un verrou du bot ne couvre pas les écritures manuelles dans ACSM.
5. Renvoyer au panneau la sanction vérifiée ou une erreur exploitable. Garder les secrets, cookies et en-têtes de session hors des journaux.

## Round ban et league ban

Réutiliser le workflow HTTP Blocklist existant. Sur de2:30505, le formulaire natif d’ajout utilise GET /blocklist avec les champs action, guid, context et duration (heures). Le retrait utilise GET /blocklist?action=remove&guid={guid}. Reprendre la valeur d’action du formulaire ou du client existant. Les ajouts et retraits planifiés utilisent le workflow Blocklist à chaud. Le worker ne doit déclencher aucun redémarrage du serveur de jeu. La clé d’exécution est le couple serveur/GUID. Le bot conserve une ligne par sanction avec son périmètre, son début, sa fin ou l’événement de fin attendu, ainsi que son état d’application et les références de l’entrée Blocklist. La portée serveur vient du routage du championnat. Le workflow planifie l’exécution d’une décision autorisée et conserve la possibilité de pratiquer avant la fenêtre du round ban. Les sanctions Servers and Discord ban suivent le processus manuel existant.

| Sanction | Ajout Blocklist | Retrait Blocklist |
| --- | --- | --- |
| Round ban | Samedi 09:00, heure Europe/Paris, pour le round concerné | Fin réelle de la course + 1 h |
| League ban | Dès application de la décision | À la date et à l’heure de fin configurées pour la ligue |

Stocker les échéances en UTC. Pour le round ban, prendre le timestamp de fin confirmé par le résultat ou validé par l’admin si la fin n’est pas disponible. Conserver le ban actif pendant que la fin reste inconnue. Si la date de fin de ligue ne comporte aucune heure, faire renseigner l’heure avant de programmer le retrait. Le démarrage immédiat du league ban est une hypothèse d’intégration.

Le worker relit les échéances en base au démarrage, traite les opérations arrivées à échéance et vérifie la présence ou l’absence du GUID après chaque écriture. Un round ban dont toute la fenêtre est passée ne doit pas produire d’ajout tardif. En cas de chevauchement, une entrée gérée par le bot reste tant qu’un motif actif la couvre. Une entrée préexistante ou posée manuellement reste sous contrôle admin. Une annulation réévalue les motifs actifs et retire l’entrée seulement si le bot en est propriétaire et qu’elle n’a plus de motif actif. Respecter les mêmes règles en cas de reprise ou de timeout.

## Vérifications faites et validation VSC

Sur GT4 1H30 ENDURANCE SERIES 2, pour le pilote de test :
- Classement : 140 → 138 avec Points Penalty = 2 → 140 avec Set Penalty = 0.
- R1 Race : 01:02:50.867 → 01:02:52.867 avec 2 s → 01:02:53.867 après Add Penalty = 3 → 01:02:50.867 après Remove Penalty. Le marqueur de pénalité a disparu.

Routes et corps relevés dans les formulaires réellement soumis avec la session admin. Blocklist a été vérifiée via l’interface admin de de2:30505. Un GUID de test absent a été ajouté avec une durée d’une heure, puis retiré. La présence et le retrait ont été vérifiés dans la liste. Le retrait était visible après un délai d’attente du navigateur, sans second clic. Le rejeu depuis le client du bot, un timeout HTTP après écriture et l’application en jeu restent à valider. Avant activation, vérifier une sanction cumulée avec annulation partielle, un timeout après écriture et deux bans qui se chevauchent.
