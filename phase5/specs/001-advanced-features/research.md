# Research: Advanced Features for TodoGenie

## Overview
This document captures research findings and technical investigations for implementing the advanced features in Phase 5 of the TodoGenie project, including recurring tasks, due date reminders, tags/categories, task sorting, Kafka integration, and Dapr.

## Recurring Tasks Implementation

### Research Findings
- **Cron Expression Libraries**: Python libraries like `croniter` can be used to parse and evaluate cron expressions for recurrence patterns
- **Job Scheduling**: Options include Celery with Redis/RabbitMQ, APScheduler, or Huey for background job processing
- **Pattern Storage**: Storing recurrence patterns as JSON allows flexibility while maintaining queryability
- **Exception Handling**: Need to consider how to handle exceptions to recurrence patterns (e.g., skipping holidays)

### Recommended Approach
- Use `croniter` for pattern evaluation
- Implement with Celery for distributed job processing
- Store patterns in a JSON field in the database
- Handle exceptions through an exception_dates array in the pattern

### Potential Challenges
- Timezone handling for recurring tasks across different regions
- Managing modifications to future instances vs. all instances of recurring tasks
- Ensuring proper cleanup of past recurring task instances

## Due Date Reminders Implementation

### Research Findings
- **Notification Types**: Browser notifications (Web Push API), email, SMS, and in-app notifications
- **Scheduling Mechanisms**: Cron jobs, database triggers, or event-driven systems
- **Delivery Reliability**: Using services like Firebase Cloud Messaging or AWS SNS for push notifications
- **Timezone Handling**: Storing user's timezone preference and scheduling reminders accordingly

### Recommended Approach
- Implement a reminder service that checks for upcoming due dates
- Use Celery Beat for periodic checks of upcoming reminders
- Support multiple notification channels (browser, email)
- Store user notification preferences

### Potential Challenges
- Handling time-sensitive notifications reliably
- Managing notification delivery when users change timezones
- Ensuring delivery of critical notifications

## Tags and Categories Implementation

### Research Findings
- **Data Modeling**: Two main approaches - storing tags as a JSON array in the task record or using a separate tags table with a many-to-many relationship
- **Performance**: JSON arrays offer faster queries but less flexibility; normalized tables offer more flexibility but require joins
- **Tag Suggestions**: Implementing autocomplete and tag suggestions to improve user experience
- **Color Coding**: Associating colors with tags for visual organization

### Recommended Approach
- Use normalized tables for tags with many-to-many relationship to tasks
- Implement caching for popular tags to improve performance
- Add tag suggestions based on user's existing tags
- Support color coding for visual distinction

### Potential Challenges
- Maintaining performance with large numbers of tags
- Handling tag renaming and its impact on existing tasks
- Preventing tag proliferation with similar meanings

## Task Sorting Implementation

### Research Findings
- **Client-Side vs Server-Side**: Client-side sorting is faster for small datasets; server-side is better for large datasets
- **Multiple Criteria**: Supporting sorting by multiple criteria simultaneously (e.g., priority first, then due date)
- **Dynamic Sorting**: Allowing users to dynamically change sorting criteria
- **Performance**: Indexing strategies for efficient sorting

### Recommended Approach
- Implement server-side sorting with configurable parameters
- Support multiple sorting criteria with priority order
- Add indexes on frequently sorted columns
- Cache sorted results for common sorting patterns

### Potential Challenges
- Balancing performance with flexibility in sorting options
- Handling sorting of complex data types (e.g., dates with time zones)
- Managing user preferences for default sorting

## Kafka Integration Research

### Research Findings
- **Python Kafka Clients**: `kafka-python`, `confluent-kafka`, and `aiokafka` are the main options
- **Performance**: `confluent-kafka` offers the best performance but is more complex; `kafka-python` is simpler but slower
- **Async Support**: `aiokafka` provides asyncio support for async Python applications
- **Schema Management**: Avro with Schema Registry is the standard for schema evolution
- **Partitioning Strategy**: Key-based partitioning ensures related events go to the same partition

### Recommended Approach
- Use `kafka-python` for simplicity and broad compatibility
- Implement JSON serialization for flexibility
- Use task/user IDs as partition keys to group related events
- Implement error handling and retry logic for resilience

### Potential Challenges
- Managing Kafka cluster in development and production environments
- Handling schema evolution as the system grows
- Ensuring message ordering within user contexts

## Dapr Integration Research

### Research Findings
- **Benefits**: Standardizes service interactions, provides building blocks, reduces vendor lock-in
- **Integration Points**: Service invocation, state management, pub/sub, bindings, secrets
- **Performance**: Sidecar architecture adds network hop overhead but provides flexibility
- **Development Experience**: Simplifies microservice development but adds operational complexity

### Recommended Approach
- Start with Dapr pub/sub for Kafka integration
- Use Dapr service invocation to replace direct HTTP calls
- Implement Dapr state management for conversation persistence
- Use Dapr secrets for configuration management

### Potential Challenges
- Learning curve for Dapr concepts and components
- Operational complexity of managing Dapr sidecars
- Debugging distributed applications with Dapr

## Architecture Considerations

### Event-Driven Architecture Benefits
- **Scalability**: Services can scale independently
- **Resilience**: Failure in one service doesn't immediately impact others
- **Flexibility**: New services can subscribe to events without modifying producers
- **Decoupling**: Loosely coupled services with well-defined contracts

### Potential Drawbacks
- **Complexity**: More complex to reason about system behavior
- **Debugging**: Distributed tracing becomes more important
- **Eventual Consistency**: May introduce consistency challenges

### Microservices vs Monolith for Phase 5
- **Current Approach**: Extend existing monolith with event-driven patterns
- **Future Consideration**: Gradually decompose into microservices as complexity grows
- **Benefits**: Easier to implement event-driven patterns in a monolith initially
- **Transition Strategy**: Use Domain-Driven Design boundaries to identify service candidates

## Security Considerations

### Data Protection
- **Encryption**: At-rest and in-transit encryption for sensitive data
- **Access Control**: Fine-grained access control for user data
- **Audit Logging**: Comprehensive logging of data access and modifications

### Kafka Security
- **Authentication**: SASL/SCRAM or Kerberos for client authentication
- **Authorization**: ACLs to control topic access
- **Encryption**: TLS for encrypting data in transit

### Dapr Security
- **Service Authentication**: mTLS between services
- **Component Security**: Secure component configurations
- **API Authorization**: Control access to Dapr endpoints

## Performance Considerations

### Scalability Factors
- **Event Volume**: Expected throughput for different event types
- **Storage Requirements**: Growth projections for event logs and state
- **Processing Latency**: Acceptable delay for event processing
- **Resource Utilization**: CPU, memory, and network requirements

### Optimization Strategies
- **Caching**: Cache frequently accessed data
- **Indexing**: Optimize database indexes for query patterns
- **Batching**: Batch event processing where appropriate
- **Partitioning**: Distribute load across multiple instances

## Testing Strategy

### Unit Testing
- Test recurrence pattern evaluation logic
- Test reminder scheduling algorithms
- Test event serialization/deserialization

### Integration Testing
- Test Kafka producer/consumer functionality
- Test Dapr component interactions
- Test end-to-end task operations with events

### Load Testing
- Simulate high event throughput
- Test system behavior under stress
- Measure response times for different operations

## Technology Stack Alignment

### Current Stack Assessment
- **Python/FastAPI**: Good fit for Kafka integration and background processing
- **Next.js**: Supports real-time updates via WebSockets for notifications
- **PostgreSQL**: Adequate for initial implementation with potential migration to more scalable options
- **Docker/Kubernetes**: Essential for managing multiple services and Dapr sidecars

### Potential Technology Additions
- **Redis**: For caching and as a Dapr state store
- **Celery**: For background job processing
- **Monitoring**: Prometheus/Grafana for metrics, Jaeger for distributed tracing