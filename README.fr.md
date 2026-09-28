# Agent Tools Check

**Votre agent IA a-t-il perdu ses outils ou sa tâche après un changement de gateway ?** Comparez les quatre étapes JSON d'un appel d'outil. La commande indique si la gateway a supprimé un outil avec espace de noms, omis de restituer son appel, modifié ses arguments ou perdu le message du sous-agent.

Français · [English](README.md) · [Español](README.es.md)

## Voir le problème en 10 secondes

```sh
python3 check.py demo --lang fr
```

La démo montre trois contrôles qui échouent sur une gateway fictive, puis le même échange qui passe après correction. Aucun modèle, compte, clé API ni réseau n'est nécessaire. Les fixtures de protocole sont **synthétiques** : il ne s'agit pas d'un test réel de Magpie ou d'une autre gateway.

## Vérifier un échange capturé

```sh
python3 check.py check examples/working-trace.json --lang fr
python3 check.py check examples/broken-trace.json --json
```

Codes de sortie : `0` conservé ; `2` capacité perdue ; `1` trace invalide. Le JSON doit contenir `client_request`, `upstream_request`, `upstream_response` et `client_response`, les quatre surfaces à capturer lors du diagnostic de votre gateway. Voir le [format des traces](docs/trace-format.md). Le vérificateur accepte un outil transmis comme `namespace__name`, exige que l'appel retourné porte son espace de noms d'origine, contrôle `encrypted_function_args: []` pour les arguments en clair et vérifie que le texte d'`agent_message` atteint la requête amont.

**Limite actuelle :** pas de capture automatique ni d'intégration Magpie. Cet outil hors ligne contrôle vos traces ; la réussite de la démo synthétique ne prouve rien sur une gateway réelle. Le contrat Responses couvert est étroit.

## Projets voisins

- [Magpie #130](https://github.com/yetone/magpie/issues/130) décrit la disparition des outils Codex avec espace de noms via Magpie. La forme concrète de `spawn_agent` guide le contrôle.
- [Magpie #141](https://github.com/yetone/magpie/issues/141) décrit un sous-agent MultiAgentV2 sans tâche reçue. Les cas `agent_message` et arguments en clair guident le contrôle des messages.
- [LLMConform](https://github.com/aitk-org/LLMConform) couvre largement la compatibilité des gateways. Agent Tools Check cible les quatre étapes d'une délégation. Aucune intégration ni affiliation n'est revendiquée.

## Tester

```sh
python3 -m unittest discover -s tests -v
```

Python 3.11+, aucune dépendance. MIT. Outil alpha de diagnostic pour mainteneurs de gateways.
