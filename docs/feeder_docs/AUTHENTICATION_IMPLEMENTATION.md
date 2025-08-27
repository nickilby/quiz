# Authentication Implementation Guide

## Overview

This document outlines the authentication implementation for PubQuiz using Supabase Auth. The system provides:

- **Quiz Master Authentication**: Required for creating and managing quizzes
- **Anonymous Participation**: Players can join quizzes without accounts
- **Row Level Security (RLS)**: Database-level security for user data
- **JWT Token Management**: Secure session handling

## Architecture

### Authentication Flow

```
1. Quiz Master Signs Up/In
   ↓
2. Supabase Auth Creates User
   ↓
3. Database Trigger Creates Quiz Master Profile
   ↓
4. RLS Policies Enforce Data Access
   ↓
5. Frontend Uses JWT for API Calls
```

### User Types

#### Quiz Masters (Authenticated)
- **Required**: Email/password authentication
- **Access**: Quiz Builder, Quiz Master Portal, Settings
- **Data**: Own quizzes, sessions, and settings
- **Security**: RLS policies restrict data access

#### Players (Anonymous)
- **Required**: No authentication needed
- **Access**: Join quizzes, participate, view scores
- **Data**: Session-specific data only
- **Security**: Public access to active sessions

## Implementation Details

### Frontend Components

#### Authentication Context (`AuthContext.tsx`)
- Manages user state throughout the app
- Handles sign in/up/logout operations
- Provides loading and error states
- Listens for auth state changes

#### Protected Routes (`ProtectedRoute.tsx`)
- Wraps quiz master features
- Redirects to login if not authenticated
- Shows loading state during auth check

#### Auth Forms
- **LoginForm**: Email/password sign in
- **SignUpForm**: New account creation with validation
- **AuthPage**: Switches between login and signup

### Backend Integration

#### Authentication Middleware (`authMiddleware.ts`)
- Verifies Supabase JWT tokens
- Adds user info to request objects
- Supports optional authentication for public endpoints

#### Database Schema Updates
- Added `auth_user_id` to `quiz_masters` table
- Created RLS policies for data security
- Added trigger to auto-create quiz master profiles

### API Security

#### Protected Endpoints
- Quiz creation, editing, deletion
- Session management
- Settings and configuration
- Admin functions

#### Public Endpoints
- Session joining
- Participant registration
- Real-time quiz participation
- Score viewing

## Database Schema

### Quiz Masters Table
```sql
ALTER TABLE quiz_masters 
ADD COLUMN auth_user_id UUID;

CREATE UNIQUE INDEX idx_quiz_masters_auth_user_id 
ON quiz_masters(auth_user_id) 
WHERE auth_user_id IS NOT NULL;
```

### RLS Policies

#### Quiz Masters
```sql
CREATE POLICY "Quiz masters can view own data" 
ON quiz_masters FOR SELECT 
USING (auth_user_id = auth.uid());
```

#### Quizzes
```sql
CREATE POLICY "Quiz masters can view own quizzes" 
ON quizzes FOR SELECT 
USING (quiz_master_id IN (
  SELECT id FROM quiz_masters WHERE auth_user_id = auth.uid()
));
```

## Environment Variables

### Frontend (.env)
```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_SERVER_URL=http://localhost:5000
```

### Backend (.env)
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Setup Instructions

### 1. Supabase Configuration

1. **Enable Auth in Supabase Dashboard**
   - Go to Authentication → Settings
   - Enable email confirmations (optional)
   - Configure email templates

2. **Run Database Migration**
   ```sql
   -- Execute update-auth-schema.sql in Supabase SQL Editor
   ```

3. **Configure RLS Policies**
   - Enable RLS on all tables
   - Apply the policies from the migration

### 2. Frontend Setup

1. **Install Dependencies**
   ```bash
   cd client
   npm install @supabase/supabase-js
   ```

2. **Configure Environment Variables**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Wrap App with AuthProvider**
   ```tsx
   <AuthProvider>
     <SettingsProvider>
       <App />
     </SettingsProvider>
   </AuthProvider>
   ```

### 3. Backend Setup

1. **Install Dependencies**
   ```bash
   cd server
   npm install @supabase/supabase-js
   ```

2. **Add Authentication Middleware**
   ```typescript
   import { authenticateUser } from './authMiddleware';
   
   // Apply to protected routes
   app.post('/api/quizzes', authenticateUser, async (req, res) => {
     // Route handler
   });
   ```

## Usage Examples

### Quiz Master Sign Up
```typescript
const { signUp } = useAuth();

const handleSignUp = async () => {
  try {
    await signUp(email, password, name);
    // User is automatically logged in
  } catch (error) {
    console.error('Sign up failed:', error);
  }
};
```

### Protected Component
```typescript
import { ProtectedRoute } from './components/Auth/ProtectedRoute';

<ProtectedRoute>
  <QuizBuilder />
</ProtectedRoute>
```

### API Call with Auth
```typescript
// Automatically includes auth headers
const quizzes = await quizAPI.getAll();
```

## Security Features

### Row Level Security (RLS)
- Users can only access their own data
- Database-level enforcement
- Automatic filtering of queries

### JWT Token Management
- Secure token storage
- Automatic token refresh
- Token validation on each request

### Session Management
- Automatic session persistence
- Secure logout
- Session timeout handling

## Testing

### Authentication Tests
```typescript
// Test sign up flow
test('should create new quiz master account', async () => {
  const { signUp } = useAuth();
  await signUp('test@example.com', 'password123', 'Test User');
  // Verify user is created and logged in
});

// Test protected routes
test('should redirect to login when not authenticated', () => {
  render(<ProtectedRoute><QuizBuilder /></ProtectedRoute>);
  expect(screen.getByText('Quiz Master Login')).toBeInTheDocument();
});
```

## Troubleshooting

### Common Issues

1. **"No token provided" error**
   - Check if user is logged in
   - Verify token is being sent in headers

2. **RLS policy violations**
   - Ensure user has proper quiz master profile
   - Check database trigger is working

3. **CORS issues**
   - Verify Supabase URL configuration
   - Check environment variables

### Debug Steps

1. **Check Authentication State**
   ```typescript
   const { user, isAuthenticated } = useAuth();
   console.log('User:', user, 'Authenticated:', isAuthenticated);
   ```

2. **Verify API Headers**
   ```typescript
   const headers = await getAuthHeaders();
   console.log('Auth headers:', headers);
   ```

3. **Check Database Policies**
   ```sql
   SELECT * FROM quiz_masters WHERE auth_user_id = auth.uid();
   ```

## Migration Guide

### From Demo Mode to Authentication

1. **Backup existing data**
2. **Run authentication migration**
3. **Create user accounts for existing quiz masters**
4. **Update frontend to require authentication**
5. **Test all functionality**

### Data Migration Script
```sql
-- Link existing quiz masters to auth users
UPDATE quiz_masters 
SET auth_user_id = 'user-uuid-here'
WHERE email = 'existing-email@example.com';
```

## Future Enhancements

### Planned Features
- **Social Login**: Google, GitHub integration
- **Password Reset**: Email-based password recovery
- **User Profiles**: Extended profile information
- **Team Management**: Multiple quiz masters per organization
- **Audit Logging**: Track user actions for security

### Security Improvements
- **Rate Limiting**: Prevent brute force attacks
- **Two-Factor Authentication**: Enhanced security
- **Session Management**: Advanced session controls
- **API Key Management**: For third-party integrations 