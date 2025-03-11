# Système de Microservices pour l'Évaluation des Prêts

## Aperçu du Projet
Ce projet implémente un **système d'évaluation des demandes de prêt** en utilisant une **architecture basée sur des microservices**. Il évalue les demandes de prêt en fonction des scores de crédit et de l’évaluation des biens immobiliers, tout en prenant des décisions automatiques grâce à la messagerie **RabbitMQ** et à la distribution des tâches avec **Celery**.

## 💡 Technologies Utilisées
- **FastAPI** : Framework d’API performant pour les microservices
- **RabbitMQ** : Courtier de messages pour la communication entre services
- **Celery** : File de tâches pour le traitement asynchrone des opérations
- **SQLite** : Base de données pour stocker les informations des clients et des prêts
- **Docker & Docker Compose** : Conteneurisation et orchestration des services
- **Uvicorn** : Serveur pour le déploiement de FastAPI

## 📂 Structure du Projet
```
loan-eval-microservices/
│── loan-service/          # Gère les demandes de prêt
│── credit-check/          # Effectue la vérification du crédit
│── property-evaluation/   # Évalue la valeur du bien immobilier
│── decision-service/      # Prend la décision d’approbation ou de rejet du prêt
│── notification-service/  # Envoie les notifications aux clients
│── insurance-service/     # Propose une assurance habitation
│── docker-compose.yml     # Orchestration des services
│── README.md              # Documentation
```

## 💻 Comment Exécuter le Projet
### Prérequis
- **Docker & Docker Compose** installés sur votre système

### 1️⃣ Construire et Exécuter Tous les Services
```bash
docker-compose up --build
```

### 2️⃣ Vérifier les Conteneurs en Exécution
```bash
docker ps
```

### 3️⃣ Accéder à l’Interface de Gestion de RabbitMQ
Le tableau de bord de **RabbitMQ** permet de surveiller les files de messages :
```
http://localhost:15672
Nom d’utilisateur : guest
Mot de passe : guest
```

## 🔄 Flux de Travail du Système
1. **L'utilisateur soumet une demande de prêt** via `loan-service`
2. **Le service de vérification de crédit** évalue la solvabilité du client
3. **Le service d’évaluation du bien** estime la valeur de la propriété
4. **Le service de décision** approuve ou rejette la demande de prêt
5. **Le service de notification** informe le client du résultat
6. **Le service d’assurance** propose une assurance habitation en cas d’approbation du prêt

## 🛠️ Points d’Entrée de l’API
### Service de Demande de Prêt
```bash
POST http://localhost:8001/loan-request/
{
    "cin": "CIN0950a",
    "montant": 150000,
    "duree": 240,
    "ville": "Paris"
}
```

### Service de Vérification de Crédit
```bash
POST http://localhost:8002/check-credit/
{
    "cin": "CIN0950a"
}
```

### Service d'Évaluation du Bien Immobilier
```bash
POST http://localhost:8003/evaluate-property/
{
    "cin": "CIN0950a",
    "ville": "Paris",
    "sqm": 100
}
```

### Service de Décision
```bash
GET http://localhost:8004/
```

### Service de Notification
```bash
GET http://localhost:8005/notifications/CIN0950a
```

### Service d’Assurance
```bash
POST http://localhost:8006/offer-insurance/
{
    "cin": "CIN0950a",
    "interested": true
}
```

## 🛠️ Débogage et Logs
Afficher les logs d’un service en cours d'exécution :
```bash
docker logs loan-container --tail=50
```
Redémarrer un conteneur défaillant :
```bash
docker restart loan-container
```

## 🚀 Améliorations Futures
- Intégration du **Machine Learning** pour une évaluation avancée du crédit
- Ajout d’une **base de données NoSQL** pour améliorer les performances
- Implémentation de **pipelines CI/CD** pour un déploiement automatisé

## 📊 Diagramme BPMN du Processus
Le processus d'évaluation des demandes de prêt est modélisé à l'aide de **BPMN (Business Process Model and Notation)**. Ce diagramme illustre les interactions entre les microservices et le flux de traitement des demandes de prêt.

![TD4 drawio](https://github.com/user-attachments/assets/a1762aa0-f001-4032-9cdd-9da7a6cce59d)



## 👥 Contributeurs
- **Ayoub SGHIR**  
- **Salma KHOLTE**

