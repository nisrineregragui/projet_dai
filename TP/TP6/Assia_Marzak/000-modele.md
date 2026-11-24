# ADR 000 : [titre de la décision]

Date : 24/11/2026 · Auteurs : Assiya MARZAK

## Contexte
Le projet nécessite un environnement de travail qui permet d'exécuter les applications avec les mêmes configurations sur différentes machines. L'installation et la configuration manuelles des dépendances peuvent provoquer des problèmes de compatibilité entre les environnements des membres du projet.

## Options étudiées
1. Installation locale : installer directement les dépendances et les outils sur chaque machine. Cette solution est simple au départ, mais peut entraîner des différences de configuration et des problèmes de compatibilité.
2. Utilisation de Docker : créer un environnement isolé et reproductible à l'aide de conteneurs. Cette solution facilite le partage de l'environnement et limite les problèmes liés aux différences entre les machines.

## Décision
L'option retenue est l'utilisation de Docker pour gérer l'environnement du projet. Ce choix permet de standardiser la configuration, de faciliter l'installation et de garantir une meilleure reproductibilité de l'environnement de travail.

## Conséquences
Points positifs : environnement plus homogène, configuration partageable et meilleure reproductibilité.

Points négatifs : nécessité d'installer et de maîtriser Docker, ainsi qu'une configuration initiale supplémentaire.

Points à surveiller : la configuration du Dockerfile, la gestion des dépendances et la compatibilité entre les environnements.
