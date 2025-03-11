# Loan Evaluation Microservices System

## 📌 Project Overview
This project implements a **loan evaluation system** using a **microservices architecture**. The system evaluates loan requests based on credit scores and property evaluations, making automatic decisions using RabbitMQ message queuing and Celery task distribution.

## Technologies Used
- **FastAPI**: API framework for high-performance microservices
- **RabbitMQ**: Message broker for service communication
- **Celery**: Task queue for asynchronous job processing
- **SQLite**: Database for storing client and loan data
- **Docker & Docker Compose**: Containerization and service orchestration
- **Uvicorn**: FastAPI server deployment

## 📂 Project Structure
```
loan-eval-microservices/
│── loan-service/          # Handles loan requests
│── credit-check/          # Performs credit verification
│── property-evaluation/   # Evaluates property worth
│── decision-service/      # Makes loan approval/rejection decisions
│── notification-service/  # Sends notifications to clients
│── insurance-service/     # Offers home insurance
│── docker-compose.yml     # Service orchestration
│── README.md              # Documentation
```

## How to Run the Project
### Prerequisites
- **Docker & Docker Compose** installed on your system

### 1 Build & Run All Services
```bash
docker-compose up --build
```

### 2️ Check Running Containers
```bash
docker ps
```

### 3️ Access RabbitMQ Management UI
RabbitMQ dashboard for monitoring message queues:
```
http://localhost:15672
Username: guest
Password: guest
```

## 🔄 Workflow of the System
1. **User submits a loan request** via `loan-service`
2. **Credit-check service** evaluates the client's creditworthiness
3. **Property-evaluation service** assesses property value
4. **Decision-service** determines loan approval/rejection
5. **Notification-service** informs the client of the decision
6. **Insurance-service** offers optional home insurance if the loan is approved

## 🛠️ API Endpoints
### Loan Request Service
```bash
POST http://localhost:8001/loan-request/
{
    "cin": "CIN0950a",
    "montant": 150000,
    "duree": 240,
    "ville": "Paris"
}
```

### Credit Check Service
```bash
POST http://localhost:8002/check-credit/
{
    "cin": "CIN0950a"
}
```

### Property Evaluation Service
```bash
POST http://localhost:8003/evaluate-property/
{
    "cin": "CIN0950a",
    "ville": "Paris",
    "sqm": 100
}
```

### Decision Service
```bash
GET http://localhost:8004/
```

### Notification Service
```bash
GET http://localhost:8005/notifications/CIN0950a
```

### Insurance Service
```bash
POST http://localhost:8006/offer-insurance/
{
    "cin": "CIN0950a",
    "interested": true
}
```

## 🛠️ Debugging & Logs
View logs of a running service:
```bash
docker logs loan-container --tail=50
```
Restart a failed container:
```bash
docker restart loan-container
```

## Future Enhancements
- Integrate **Machine Learning** for advanced credit scoring
- Add **NoSQL Database** for better performance
- Implement **CI/CD pipelines** for automated deployment

## Contributors
- **Ayoub SGHIR** 
- **Salma KHOLTE**
