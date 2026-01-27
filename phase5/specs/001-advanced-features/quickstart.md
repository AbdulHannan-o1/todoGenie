# Quickstart Guide: Advanced Features for TodoGenie

## Overview
This guide provides instructions for setting up and running the Phase 5 advanced features of the TodoGenie application, including recurring tasks, due date reminders, tags/categories, task sorting, Kafka integration, and Dapr.

## Prerequisites

### System Requirements
- Docker and Docker Compose (v2.0+)
- Minikube or access to a Kubernetes cluster
- Node.js (v18+) and npm/yarn
- Python (v3.11+)
- Java (v11+) for Kafka
- Dapr CLI installed and initialized

### Environment Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd todoGenie
   ```

2. Navigate to the Phase 5 directory:
   ```bash
   cd phase5
   ```

3. Install Python dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## Setting Up Kafka

### Local Kafka Setup
1. Start Kafka using Docker Compose:
   ```bash
   docker-compose -f kafka-docker-compose.yml up -d
   ```

2. Verify Kafka is running:
   ```bash
   docker-compose -f kafka-docker-compose.yml ps
   ```

3. Create required Kafka topics:
   ```bash
   docker exec -it kafka-container kafka-topics --create --topic task-events --bootstrap-server localhost:9092
   docker exec -it kafka-container kafka-topics --create --topic reminders --bootstrap-server localhost:9092
   docker exec -it kafka-container kafka-topics --create --topic task-updates --bootstrap-server localhost:9092
   ```

### Kafka Configuration
Update your environment variables to point to the Kafka cluster:
```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
TASK_EVENTS_TOPIC=task-events
REMINDERS_TOPIC=reminders
TASK_UPDATES_TOPIC=task-updates
```

## Setting Up Dapr

### Initialize Dapr
1. Initialize Dapr locally:
   ```bash
   dapr init
   ```

2. Verify Dapr is running:
   ```bash
   dapr status
   ```

### Dapr Components Setup
Create the following Dapr component files in the `dapr/components` directory:

#### Kafka Pub/Sub Component (`kafka-pubsub.yaml`)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "dapr-consumer-group"
  - name: authRequired
    value: "false"
```

#### State Store Component (`statestore.yaml`)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: localhost:6379
  - name: redisPassword
    value: ""
```

#### Secret Store Component (`secretstore.yaml`)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: /path/to/secrets.json
```

## Running the Application

### Option 1: Local Development
1. Set up environment variables:
   ```bash
   cp .env.example .env
   # Update .env with appropriate values
   ```

2. Start the backend with Dapr:
   ```bash
   cd backend
   dapr run --app-id backend --app-port 8000 -- uvicorn main:app --reload
   ```

3. In a new terminal, start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

4. Start the Kafka consumers:
   ```bash
   cd backend
   dapr run --app-id kafka-consumer -- python src/services/kafka_consumer.py
   ```

### Option 2: Docker Compose
1. Build the Docker images:
   ```bash
   docker-compose -f docker-compose.phase5.yml build
   ```

2. Start all services:
   ```bash
   docker-compose -f docker-compose.phase5.yml up -d
   ```

### Option 3: Kubernetes with Minikube
1. Start Minikube:
   ```bash
   minikube start
   ```

2. Install Dapr in Kubernetes:
   ```bash
   dapr init -k
   ```

3. Apply Dapr components:
   ```bash
   kubectl apply -f dapr/components/
   ```

4. Deploy the application:
   ```bash
   kubectl apply -f k8s/
   ```

## Configuration

### Environment Variables
Required environment variables for Phase 5:

Backend:
```
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
TASK_EVENTS_TOPIC=task-events
REMINDERS_TOPIC=reminders
TASK_UPDATES_TOPIC=task-updates
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
JWT_SECRET=your-super-secret-jwt-key-here
```

Frontend:
```
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
NEXT_PUBLIC_KAFKA_ENABLED=true
NEXT_PUBLIC_DAPR_ENABLED=true
```

## Key Features Setup

### Recurring Tasks
1. The recurrence engine will automatically process recurring tasks based on their patterns
2. Configure the recurrence job scheduler in the backend settings
3. Set up cron expressions for checking recurring tasks (e.g., every 5 minutes)

### Due Date Reminders
1. The reminder service will process tasks with due dates
2. Configure notification channels (browser, email, etc.)
3. Set up the reminder job scheduler to run at appropriate intervals

### Tags and Categories
1. Users can create and assign tags to tasks
2. Tags are user-specific and support color coding
3. Tasks can have multiple tags assigned

### Task Sorting
1. Tasks can be sorted by due date, priority, or alphabetically
2. Sorting options are available in the UI
3. Backend API supports sorting parameters

## Testing the Setup

### Verify Kafka Connectivity
```bash
# Publish a test event
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"eventType": "test", "data": {"message": "Hello Kafka"}}'
```

### Verify Dapr Components
```bash
# Check Dapr sidecar health
curl http://localhost:3501/v1.0/healthz
```

### Test API Endpoints
```bash
# Test recurring task creation
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly Team Meeting",
    "recurrence_pattern": {
      "frequency": "weekly",
      "interval": 1,
      "end_condition": {"type": "never"}
    }
  }'

# Test task with due date and reminder
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Submit Report",
    "due_date": "2023-12-25T10:00:00Z",
    "reminder_time": "2023-12-25T09:00:00Z"
  }'
```

## Troubleshooting

### Common Issues
1. **Kafka Connection Issues**: Verify that Kafka is running and the broker address is correct
2. **Dapr Not Initialized**: Run `dapr uninstall` followed by `dapr init`
3. **Database Connection Issues**: Check that the database server is running and credentials are correct
4. **Port Conflicts**: Ensure required ports (8000, 3500, 3501, 9092) are available

### Useful Commands
```bash
# Check running Docker containers
docker ps

# View application logs
docker-compose -f docker-compose.phase5.yml logs

# Check Dapr status
dapr status -k

# List Dapr components
kubectl get components.dapr.io
```

## Next Steps
1. Implement the advanced features according to the tasks outlined in `tasks.md`
2. Set up monitoring and observability for Kafka and Dapr
3. Configure production-level security settings
4. Set up CI/CD pipelines for automated deployment