# Scaling & Performance Guide

## Overview

This document outlines the scaling strategies and performance considerations for the PubQuiz application, designed to support hundreds of concurrent quiz masters and thousands of participants.

## Current Architecture

### WebSocket Scaling

The application currently supports:

- **Concurrent Connections**: 100+ simultaneous WebSocket connections per server instance
- **Message Throughput**: 1000+ messages per second
- **Session Management**: 50+ concurrent quiz sessions
- **Memory Efficiency**: <100MB increase for 200 connections
- **Response Time**: <50ms for real-time updates

### Performance Benchmarks

Based on load testing results:

| Metric | Current Capacity | Target Capacity |
|--------|------------------|-----------------|
| Concurrent Connections | 100 | 1000+ |
| Sessions per Server | 50 | 500+ |
| Messages/Second | 1000 | 10000+ |
| Memory Usage | <100MB/200 conn | <500MB/1000 conn |
| Response Time | <50ms | <25ms |

## Scaling Strategies

### 1. Horizontal Scaling

#### WebSocket Server Scaling

**Current Implementation:**
- Single server instance handling all WebSocket connections
- In-memory session and participant tracking
- Direct database queries for each operation

**Scaling Approach:**
```typescript
// Multiple server instances with load balancer
const servers = [
  { port: 5000, instance: 'server-1' },
  { port: 5001, instance: 'server-2' },
  { port: 5002, instance: 'server-3' }
];

// Load balancer configuration
const loadBalancer = {
  algorithm: 'least-connections',
  healthCheck: '/health',
  stickySessions: true // Keep users on same server
};
```

#### Database Scaling

**Current Implementation:**
- Direct Supabase queries for each operation
- No caching layer
- Single database connection

**Scaling Approach:**
```typescript
// Database connection pooling
const dbPool = {
  min: 5,
  max: 20,
  acquireTimeout: 30000,
  idleTimeout: 60000
};

// Read replicas for read-heavy operations
const readReplicas = [
  'supabase-read-1',
  'supabase-read-2',
  'supabase-read-3'
];
```

### 2. Caching Strategy

#### Redis Implementation

**Session Caching:**
```typescript
// Cache session state
await redis.setex(`session:${sessionId}`, 3600, JSON.stringify(sessionState));

// Cache participant list
await redis.setex(`participants:${sessionId}`, 300, JSON.stringify(participants));

// Cache scores
await redis.setex(`scores:${sessionId}`, 60, JSON.stringify(scores));
```

**Question Caching:**
```typescript
// Cache quiz questions
await redis.setex(`quiz:${quizId}`, 7200, JSON.stringify(quizData));

// Cache AI-generated questions
await redis.setex(`ai-questions:${topic}`, 3600, JSON.stringify(questions));
```

#### Memory Caching

**In-Memory Session Store:**
```typescript
class SessionStore {
  private sessions = new Map<string, SessionData>();
  private participants = new Map<string, Participant[]>();
  private scores = new Map<string, Score[]>();

  // Fast in-memory operations
  getSession(sessionId: string): SessionData | undefined {
    return this.sessions.get(sessionId);
  }

  updateScores(sessionId: string, scores: Score[]): void {
    this.scores.set(sessionId, scores);
  }
}
```

### 3. Database Optimization

#### Indexing Strategy

**Current Indexes:**
```sql
-- Session lookups
CREATE INDEX idx_quiz_sessions_status ON quiz_sessions(status);
CREATE INDEX idx_quiz_sessions_quiz_id ON quiz_sessions(quiz_id);

-- Participant queries
CREATE INDEX idx_participants_session_id ON participants(session_id);
CREATE INDEX idx_participants_name ON participants(name);

-- Answer queries
CREATE INDEX idx_answers_session_id ON answers(session_id);
CREATE INDEX idx_answers_participant_id ON answers(participant_id);
CREATE INDEX idx_answers_question_id ON answers(question_id);
```

**Additional Indexes for Scaling:**
```sql
-- Composite indexes for common queries
CREATE INDEX idx_answers_session_participant ON answers(session_id, participant_id);
CREATE INDEX idx_answers_session_question ON answers(session_id, question_id);

-- Partial indexes for active sessions
CREATE INDEX idx_quiz_sessions_active ON quiz_sessions(id) WHERE status = 'active';

-- Time-based indexes
CREATE INDEX idx_answers_answered_at ON answers(answered_at);
```

#### Query Optimization

**Batch Operations:**
```typescript
// Batch score updates
const batchUpdateScores = async (sessionId: string, scores: Score[]) => {
  const updates = scores.map(score => ({
    participant_id: score.participantId,
    session_id: sessionId,
    total_score: score.score,
    correct_answers: score.correctAnswers
  }));

  await supabase
    .from('participant_scores')
    .upsert(updates, { onConflict: 'participant_id,session_id' });
};
```

**Connection Pooling:**
```typescript
// Database connection pool
const dbPool = {
  min: 10,
  max: 50,
  acquireTimeout: 30000,
  idleTimeout: 60000,
  reapInterval: 1000
};
```

### 4. Load Balancing

#### WebSocket Load Balancer

**Nginx Configuration:**
```nginx
upstream websocket_servers {
    least_conn;
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    server_name pubquiz.example.com;

    location /socket.io/ {
        proxy_pass http://websocket_servers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Sticky sessions
        proxy_cookie_path / "/; HTTPOnly; Secure";
    }
}
```

#### API Load Balancer

**Express.js with Cluster:**
```typescript
import cluster from 'cluster';
import os from 'os';

if (cluster.isMaster) {
  const numCPUs = os.cpus().length;
  
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork();
  });
} else {
  // Worker process
  const app = express();
  const server = createServer(app);
  const wsService = new WebSocketService(server);
  
  server.listen(process.env.PORT || 5000);
}
```

### 5. Monitoring & Observability

#### Performance Monitoring

**Metrics Collection:**
```typescript
class PerformanceMonitor {
  private metrics = {
    connections: 0,
    messagesPerSecond: 0,
    responseTime: 0,
    memoryUsage: 0,
    activeSessions: 0
  };

  recordConnection(): void {
    this.metrics.connections++;
  }

  recordMessage(): void {
    this.metrics.messagesPerSecond++;
  }

  recordResponseTime(time: number): void {
    this.metrics.responseTime = time;
  }

  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }
}
```

**Health Checks:**
```typescript
// Health check endpoint
app.get('/health', (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    connections: wsService.getTotalConnectedClients(),
    sessions: wsService.getActiveSessions()
  };

  res.json(health);
});
```

#### Logging Strategy

**Structured Logging:**
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Log WebSocket events
logger.info('WebSocket event', {
  event: 'participant-joined',
  sessionId: 'session-123',
  participantId: 'participant-456',
  timestamp: new Date().toISOString()
});
```

## Implementation Roadmap

### Phase 1: Foundation (Current)
- ✅ WebSocket implementation with Socket.IO
- ✅ Basic session management
- ✅ Rate limiting and validation
- ✅ Comprehensive testing suite

### Phase 2: Caching & Optimization (Next)
- 🔄 Redis integration for session caching
- 🔄 Database query optimization
- 🔄 Connection pooling
- 🔄 Memory usage optimization

### Phase 3: Horizontal Scaling (Future)
- 📋 Load balancer implementation
- 📋 Multiple server instances
- 📋 Shared state management
- 📋 Database read replicas

### Phase 4: Advanced Features (Future)
- 📋 Message queuing with persistence
- 📋 Advanced monitoring and analytics
- 📋 Auto-scaling capabilities
- 📋 Geographic distribution

## Performance Testing

### Load Testing Tools

**Artillery.js Configuration:**
```yaml
config:
  target: 'http://localhost:5000'
  phases:
    - duration: 60
      arrivalRate: 10
    - duration: 120
      arrivalRate: 50
    - duration: 60
      arrivalRate: 100

scenarios:
  - name: "WebSocket connections"
    engine: "socketio"
    flow:
      - connect:
          url: "http://localhost:5000"
      - emit:
          channel: "join-session"
          data: "session-123"
      - think: 5
      - emit:
          channel: "participant-join"
          data:
            sessionId: "session-123"
            name: "Test User"
            team: "Test Team"
```

**K6 Configuration:**
```javascript
import ws from 'k6/ws';
import { check } from 'k6';

export default function () {
  const url = 'ws://localhost:5000/socket.io/';
  const params = { tags: { my_tag: 'hello' } };

  const res = ws.connect(url, params, function (socket) {
    socket.on('open', () => {
      socket.send(JSON.stringify({
        event: 'join-session',
        data: 'session-123'
      }));
    });

    socket.on('message', (data) => {
      console.log('Received:', data);
    });

    socket.on('close', () => {
      console.log('Connection closed');
    });
  });

  check(res, { 'status is 101': (r) => r && r.status === 101 });
}
```

### Performance Benchmarks

**Connection Load Test:**
```bash
# Test 100 concurrent connections
npm run test:load:connections -- --connections=100 --duration=60

# Test 500 rapid connections
npm run test:load:rapid -- --connections=500 --duration=30
```

**Message Throughput Test:**
```bash
# Test 1000 messages per second
npm run test:load:messages -- --messages=1000 --duration=60

# Test sustained load
npm run test:load:sustained -- --duration=300 --rate=100
```

## Deployment Considerations

### Containerization

**Docker Configuration:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 5000

CMD ["npm", "start"]
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Environment Configuration

**Production Environment:**
```env
# Server Configuration
NODE_ENV=production
PORT=5000
CLIENT_URL=https://pubquiz.example.com

# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your-redis-password

# Monitoring
LOG_LEVEL=info
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30000
```

## Best Practices

### Code Optimization

1. **Use Connection Pooling**: Reuse database connections
2. **Implement Caching**: Cache frequently accessed data
3. **Batch Operations**: Group database operations
4. **Optimize Queries**: Use proper indexes and query patterns
5. **Memory Management**: Clean up resources properly

### Infrastructure

1. **Load Balancing**: Distribute traffic across multiple servers
2. **Auto-scaling**: Scale based on demand
3. **Monitoring**: Track performance metrics
4. **Backup Strategy**: Regular database backups
5. **Security**: Implement proper authentication and authorization

### Development

1. **Testing**: Comprehensive load testing
2. **Profiling**: Monitor performance bottlenecks
3. **Documentation**: Keep scaling documentation updated
4. **Code Review**: Review for performance implications
5. **Monitoring**: Implement proper logging and metrics

## Troubleshooting

### Common Scaling Issues

1. **Memory Leaks**
   - Monitor memory usage
   - Clean up event listeners
   - Implement proper garbage collection

2. **Connection Limits**
   - Increase file descriptor limits
   - Use connection pooling
   - Implement connection timeouts

3. **Database Bottlenecks**
   - Optimize queries
   - Add proper indexes
   - Use read replicas

4. **Network Issues**
   - Monitor bandwidth usage
   - Implement compression
   - Use CDN for static assets

### Performance Tuning

1. **WebSocket Optimization**
   - Use binary messages for large data
   - Implement message compression
   - Optimize event handling

2. **Database Optimization**
   - Use connection pooling
   - Implement query caching
   - Optimize schema design

3. **Memory Optimization**
   - Monitor memory usage
   - Implement proper cleanup
   - Use streaming for large datasets

## Future Considerations

### Advanced Scaling Features

1. **Microservices Architecture**
   - Split into smaller services
   - Independent scaling
   - Service mesh implementation

2. **Event-Driven Architecture**
   - Message queues
   - Event sourcing
   - CQRS pattern

3. **Geographic Distribution**
   - Multi-region deployment
   - CDN integration
   - Edge computing

4. **Machine Learning Integration**
   - Predictive scaling
   - Anomaly detection
   - Performance optimization

### Technology Evolution

1. **WebSocket Alternatives**
   - Server-Sent Events (SSE)
   - WebRTC for peer-to-peer
   - GraphQL subscriptions

2. **Database Evolution**
   - Time-series databases
   - Graph databases
   - Distributed databases

3. **Infrastructure Evolution**
   - Serverless architecture
   - Edge computing
   - Container orchestration 