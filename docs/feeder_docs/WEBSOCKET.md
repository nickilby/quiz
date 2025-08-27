# WebSocket Architecture & Implementation

## Overview

The PubQuiz application uses Socket.IO for real-time communication between quiz masters and participants. This document provides a comprehensive guide to the WebSocket architecture, events, and implementation details.

## Architecture

### Server-Side Implementation

The WebSocket service is implemented in `server/src/websocket.ts` and provides:

- **Real-time Communication**: Instant message delivery between clients
- **Session Management**: Track active sessions and participants
- **Role-Based Access Control**: Different permissions for quiz masters and participants
- **Rate Limiting**: Protection against abuse and spam
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Performance Monitoring**: Real-time connection and session monitoring

### Client-Side Implementation

The WebSocket client is implemented in `client/src/services/websocket.ts` and provides:

- **Automatic Reconnection**: Handles network interruptions gracefully
- **Event Buffering**: Queues messages during disconnections
- **Real-time Updates**: Instant synchronization of quiz state
- **Connection Monitoring**: Real-time connection status and health checks

## WebSocket Events

### Client to Server Events

#### Session Management

**`join-session`**
```typescript
// Join a quiz session
socket.emit('join-session', sessionId: string)
```
- **Purpose**: Join a specific quiz session
- **Parameters**: `sessionId` - The unique session identifier
- **Response**: Receives current session state and participants list
- **Validation**: Session ID must be valid and session must exist

**`leave-session`**
```typescript
// Leave a quiz session
socket.emit('leave-session', sessionId: string)
```
- **Purpose**: Leave a quiz session
- **Parameters**: `sessionId` - The session to leave
- **Response**: No response, socket leaves the session room

#### Participant Management

**`participant-join`**
```typescript
// Join as a participant
socket.emit('participant-join', {
  sessionId: string,
  name: string,
  team?: string
})
```
- **Purpose**: Register as a participant in a session
- **Parameters**: 
  - `sessionId` - Session identifier
  - `name` - Participant name (1-50 characters)
  - `team` - Optional team name (1-50 characters)
- **Response**: Broadcasts participant joined event to all session members
- **Validation**: Name is required, team is optional

#### Answer Submission

**`submit-answer`**
```typescript
// Submit an answer to a question
socket.emit('submit-answer', {
  sessionId: string,
  questionId: string,
  participantId: string,
  answer: number // 0-3 for multiple choice
})
```
- **Purpose**: Submit an answer to the current question
- **Parameters**:
  - `sessionId` - Session identifier
  - `questionId` - Question identifier
  - `participantId` - Participant identifier
  - `answer` - Selected answer (0-3 for multiple choice)
- **Response**: Broadcasts answer submitted event and updates scores
- **Validation**: Answer must be 0-3, prevents duplicate submissions

#### Quiz Control (Quiz Master Only)

**`start-quiz`**
```typescript
// Start the quiz
socket.emit('start-quiz', sessionId: string)
```
- **Purpose**: Start the quiz session
- **Parameters**: `sessionId` - Session identifier
- **Response**: Broadcasts quiz started event and updates session state
- **Permissions**: Only quiz masters can start quizzes

**`next-question`**
```typescript
// Move to next question
socket.emit('next-question', sessionId: string)
```
- **Purpose**: Advance to the next question
- **Parameters**: `sessionId` - Session identifier
- **Response**: Broadcasts question changed event and updates session state
- **Permissions**: Only quiz masters can control question flow

**`show-answer`**
```typescript
// Show the correct answer
socket.emit('show-answer', sessionId: string)
```
- **Purpose**: Reveal the correct answer to the current question
- **Parameters**: `sessionId` - Session identifier
- **Response**: Broadcasts answer revealed event and updates session state
- **Permissions**: Only quiz masters can show answers

### Server to Client Events

#### Session Updates

**`session-state-changed`**
```typescript
// Session state update
socket.on('session-state-changed', (state: SessionState) => {
  // Handle session state changes
})
```
- **Purpose**: Notify clients of session state changes
- **Data**: Current session state including round, question, status, etc.

**`session-updated`**
```typescript
// Session information update
socket.on('session-updated', (session: QuizSession) => {
  // Handle session updates
})
```
- **Purpose**: Notify clients of session information changes
- **Data**: Updated session information

#### Participant Updates

**`participant-joined`**
```typescript
// New participant joined
socket.on('participant-joined', (participant: Participant) => {
  // Handle new participant
})
```
- **Purpose**: Notify when a new participant joins
- **Data**: Participant information

**`participant-left`**
```typescript
// Participant left
socket.on('participant-left', (participantId: string) => {
  // Handle participant leaving
})
```
- **Purpose**: Notify when a participant leaves
- **Data**: Participant ID

**`participants-updated`**
```typescript
// Updated participants list
socket.on('participants-updated', (participants: Participant[]) => {
  // Handle participants list update
})
```
- **Purpose**: Notify of updated participants list
- **Data**: Array of all participants in the session

#### Quiz Flow

**`quiz-started`**
```typescript
// Quiz has started
socket.on('quiz-started', () => {
  // Handle quiz start
})
```
- **Purpose**: Notify that the quiz has started
- **Data**: No data, just notification

**`question-changed`**
```typescript
// New question displayed
socket.on('question-changed', (question: Question) => {
  // Handle new question
})
```
- **Purpose**: Notify of new question
- **Data**: Question information

**`answer-revealed`**
```typescript
// Correct answer shown
socket.on('answer-revealed', (correctAnswer: number) => {
  // Handle answer reveal
})
```
- **Purpose**: Notify that the correct answer has been revealed
- **Data**: Correct answer number (0-3)

#### Answer Updates

**`answer-submitted`**
```typescript
// Answer submitted by participant
socket.on('answer-submitted', (data: {
  participantId: string,
  questionId: string,
  answer: number
}) => {
  // Handle answer submission
})
```
- **Purpose**: Notify when an answer is submitted
- **Data**: Participant ID, question ID, and submitted answer

**`scores-updated`**
```typescript
// Updated leaderboard
socket.on('scores-updated', (scores: Score[]) => {
  // Handle score updates
})
```
- **Purpose**: Notify of updated scores and leaderboard
- **Data**: Array of participant scores sorted by rank

#### Error Handling

**`error`**
```typescript
// Error message
socket.on('error', (error: {
  message: string,
  code?: string
}) => {
  // Handle error
})
```
- **Purpose**: Notify of errors
- **Data**: Error message and optional error code

## Implementation Details

### Rate Limiting

The WebSocket service implements rate limiting to prevent abuse:

- **Limit**: 100 requests per minute per socket
- **Window**: 1-minute sliding window
- **Action**: Rejects requests that exceed the limit
- **Monitoring**: Logs rate limit violations

### Input Validation

All WebSocket events are validated before processing:

- **Session IDs**: Must be non-empty strings ≤100 characters
- **Participant Names**: Must be 1-50 characters
- **Team Names**: Optional, must be ≤50 characters if provided
- **Answers**: Must be numbers 0-3 for multiple choice
- **Question IDs**: Must be valid UUIDs

### Error Handling

Comprehensive error handling ensures graceful degradation:

- **Database Errors**: Handled gracefully with user-friendly messages
- **Validation Errors**: Clear error messages with specific details
- **Network Errors**: Automatic reconnection and message buffering
- **Permission Errors**: Clear indication of insufficient permissions

### Session Management

The service tracks active sessions and participants:

- **Session Rooms**: Socket.IO rooms for each session
- **Participant Tracking**: Maps socket IDs to participant information
- **Role Management**: Tracks quiz master vs participant roles
- **Cleanup**: Automatic cleanup on disconnection

### Performance Optimizations

Several optimizations ensure high performance:

- **Database Queries**: Optimized queries with proper indexing
- **Memory Management**: Efficient cleanup of disconnected sockets
- **Message Broadcasting**: Targeted broadcasting to session rooms only
- **Connection Limits**: Configurable connection limits per session

## Usage Examples

### Basic Connection

```typescript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to WebSocket server');
});

socket.on('disconnect', () => {
  console.log('Disconnected from WebSocket server');
});
```

### Joining a Session

```typescript
// Join a session
socket.emit('join-session', 'session-123');

// Listen for session state updates
socket.on('session-state-changed', (state) => {
  console.log('Session state:', state);
});

// Listen for participants updates
socket.on('participants-updated', (participants) => {
  console.log('Participants:', participants);
});
```

### Joining as Participant

```typescript
// Join as a participant
socket.emit('participant-join', {
  sessionId: 'session-123',
  name: 'John Doe',
  team: 'Team Alpha'
});

// Listen for participant joined confirmation
socket.on('participant-joined', (participant) => {
  console.log('Joined as:', participant);
});
```

### Submitting Answers

```typescript
// Submit an answer
socket.emit('submit-answer', {
  sessionId: 'session-123',
  questionId: 'question-456',
  participantId: 'participant-789',
  answer: 2 // Option C
});

// Listen for answer confirmation
socket.on('answer-submitted', (data) => {
  console.log('Answer submitted:', data);
});

// Listen for score updates
socket.on('scores-updated', (scores) => {
  console.log('Updated scores:', scores);
});
```

### Quiz Master Controls

```typescript
// Start the quiz
socket.emit('start-quiz', 'session-123');

// Listen for quiz start confirmation
socket.on('quiz-started', () => {
  console.log('Quiz has started');
});

// Move to next question
socket.emit('next-question', 'session-123');

// Listen for question changes
socket.on('question-changed', (question) => {
  console.log('New question:', question);
});

// Show correct answer
socket.emit('show-answer', 'session-123');

// Listen for answer reveal
socket.on('answer-revealed', (correctAnswer) => {
  console.log('Correct answer:', correctAnswer);
});
```

### Error Handling

```typescript
// Listen for errors
socket.on('error', (error) => {
  console.error('WebSocket error:', error.message);
  
  switch (error.code) {
    case 'RATE_LIMIT_EXCEEDED':
      console.log('Too many requests, please slow down');
      break;
    case 'INVALID_SESSION_ID':
      console.log('Invalid session ID');
      break;
    case 'PERMISSION_DENIED':
      console.log('Insufficient permissions');
      break;
    default:
      console.log('Unknown error occurred');
  }
});
```

## Testing

The WebSocket implementation includes comprehensive testing:

### Unit Tests
- Event handling validation
- Input validation
- Error handling
- Session management

### Integration Tests
- Real Socket.IO connections
- End-to-end communication
- Multi-client scenarios

### Load Tests
- Concurrent connections
- Message throughput
- Memory usage
- Performance benchmarks

Run tests with:
```bash
npm run test:websocket:all
```

## Monitoring and Debugging

### Server-Side Monitoring

The WebSocket service provides monitoring methods:

```typescript
// Get total connected clients
const totalClients = wsService.getTotalConnectedClients();

// Get active sessions count
const activeSessions = wsService.getActiveSessions();

// Get connected clients for a session
const sessionClients = wsService.getConnectedClients('session-123');

// Get session information for a socket
const sessionInfo = wsService.getSessionInfo('socket-id');
```

### Client-Side Monitoring

Monitor connection status and health:

```typescript
// Connection status
socket.connected // boolean

// Connection events
socket.on('connect', () => {
  console.log('Connected');
});

socket.on('disconnect', () => {
  console.log('Disconnected');
});

socket.on('reconnect', (attemptNumber) => {
  console.log('Reconnected after', attemptNumber, 'attempts');
});

socket.on('reconnect_error', (error) => {
  console.log('Reconnection error:', error);
});
```

## Best Practices

### Client-Side

1. **Always handle connection events**
2. **Implement proper error handling**
3. **Use event listeners consistently**
4. **Clean up listeners on component unmount**
5. **Handle reconnection gracefully**

### Server-Side

1. **Validate all input data**
2. **Implement proper error handling**
3. **Use rate limiting to prevent abuse**
4. **Monitor memory usage**
5. **Clean up resources on disconnect**

### Performance

1. **Limit message frequency**
2. **Use targeted broadcasting**
3. **Implement proper indexing**
4. **Monitor connection limits**
5. **Optimize database queries**

## Troubleshooting

### Common Issues

1. **Connection refused**
   - Check server is running
   - Verify WebSocket URL
   - Check firewall settings

2. **CORS errors**
   - Verify CORS configuration
   - Check client URL settings

3. **Rate limiting**
   - Reduce message frequency
   - Implement client-side throttling

4. **Memory leaks**
   - Clean up event listeners
   - Monitor connection cleanup

5. **Performance issues**
   - Check database queries
   - Monitor memory usage
   - Verify connection limits

### Debugging

Enable debug logging:

```typescript
// Client-side
const socket = io('http://localhost:5000', {
  debug: true
});

// Server-side
const wsService = new WebSocketService(httpServer);
// Debug logs are automatically enabled in development
```

## Future Enhancements

Planned improvements for the WebSocket implementation:

1. **Redis Integration**: Shared state across multiple server instances
2. **Message Queuing**: Reliable message delivery with persistence
3. **Compression**: Message compression for bandwidth optimization
4. **Encryption**: End-to-end encryption for sensitive data
5. **Analytics**: Detailed usage analytics and monitoring
6. **Load Balancing**: Horizontal scaling with multiple server instances 