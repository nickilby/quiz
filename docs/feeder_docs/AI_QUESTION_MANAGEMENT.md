# AI Question Management

## Overview

The AI Question Management system provides intelligent control over how AI-generated questions are reused to maintain freshness and variety while reducing API costs. This system addresses the issue of repetitive questions by implementing configurable reuse policies.

## Features

### 🎯 **Smart Question Reuse**
- **Configurable Reuse Percentage**: Control how many questions can come from saved database (default: 20%)
- **Time-based Freshness**: Questions won't be reused for a specified number of days (default: 90 days)
- **Usage Count Limits**: Prevent overuse by limiting how many times a question can be reused (default: 5 times)
- **Difficulty Tolerance**: Match questions within a configurable difficulty range (default: ±10 points)

### 🔧 **Advanced Settings**
- **Enable/Disable Reuse**: Toggle question reuse on or off
- **Percentage Control**: Set maximum percentage of reused questions (0-100%)
- **Freshness TTL**: Configure how long questions stay "fresh" (1-365 days)
- **Usage Limits**: Set maximum reuse count per question (1-50 times)
- **Difficulty Matching**: Configure difficulty range tolerance (±1-50 points)

## How It Works

### 1. **Question Generation Process**
When generating questions, the system:

1. **Calculates Reuse Allowance**: Determines how many questions can be reused based on percentage setting
2. **Queries Database**: Searches for eligible questions that meet freshness and usage criteria
3. **Mixes Questions**: Combines reused questions with newly generated ones
4. **Updates Usage**: Tracks when questions are reused and increments usage counts

### 2. **Eligibility Criteria**
A question is eligible for reuse if:
- ✅ Subject matches the requested topic
- ✅ Difficulty score is within tolerance range
- ✅ Usage count is below maximum limit
- ✅ Last used date is older than freshness threshold
- ✅ AI reuse is enabled in settings

### 3. **Database Schema**
```sql
-- AI Question Templates Table
CREATE TABLE ai_question_templates (
  id UUID PRIMARY KEY,
  subject TEXT NOT NULL,
  difficulty_score INTEGER NOT NULL, -- 1-100 scale
  question TEXT NOT NULL,
  options TEXT[] NOT NULL,
  correct_answer INTEGER NOT NULL,
  explanation TEXT,
  ai_source TEXT NOT NULL, -- 'anthropic', 'openai', etc.
  ai_prompt TEXT,
  usage_count INTEGER DEFAULT 0, -- Times reused
  last_used_at TIMESTAMP, -- Last reuse date
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## Configuration

### **Default Settings**
```typescript
const defaultAISettings = {
  aiQuestionReuseEnabled: true,        // Enable reuse
  aiQuestionReusePercentage: 20,       // 20% max reuse
  aiQuestionFreshnessDays: 90,         // 90 days TTL
  aiQuestionMaxUsageCount: 5,          // Max 5 reuses
  aiQuestionDifficultyTolerance: 10    // ±10 difficulty points
};
```

### **Settings Interface**
```typescript
interface QuizMasterSettings {
  // ... existing settings ...
  
  // AI Question Management Settings
  aiQuestionReuseEnabled: boolean;
  aiQuestionReusePercentage: number; // 0-100
  aiQuestionFreshnessDays: number;   // 1-365
  aiQuestionMaxUsageCount: number;   // 1-50
  aiQuestionDifficultyTolerance: number; // 1-50
}
```

## Usage Examples

### **Scenario 1: Fresh Questions Only**
```typescript
// Generate 10 questions with no reuse
const questions = await aiService.generateQuestions({
  subject: 'Science',
  difficulty: 50,
  questionCount: 10,
  aiQuestionReuseEnabled: false
});
// Result: 10 new AI-generated questions
```

### **Scenario 2: Balanced Mix**
```typescript
// Generate 10 questions with 30% reuse
const questions = await aiService.generateQuestions({
  subject: 'Science',
  difficulty: 50,
  questionCount: 10,
  aiQuestionReuseEnabled: true,
  aiQuestionReusePercentage: 30,
  aiQuestionFreshnessDays: 60,
  aiQuestionMaxUsageCount: 3
});
// Result: ~3 reused + 7 new questions
```

### **Scenario 3: Maximum Reuse**
```typescript
// Generate 10 questions with 80% reuse
const questions = await aiService.generateQuestions({
  subject: 'Science',
  difficulty: 50,
  questionCount: 10,
  aiQuestionReuseEnabled: true,
  aiQuestionReusePercentage: 80,
  aiQuestionFreshnessDays: 30,
  aiQuestionMaxUsageCount: 10
});
// Result: ~8 reused + 2 new questions
```

## API Endpoints

### **Generate Questions with AI Management**
```http
POST /api/ai/generate-questions
Content-Type: application/json

{
  "subject": "Science",
  "difficulty": 50,
  "questionCount": 10,
  "aiQuestionReuseEnabled": true,
  "aiQuestionReusePercentage": 20,
  "aiQuestionFreshnessDays": 90,
  "aiQuestionMaxUsageCount": 5,
  "aiQuestionDifficultyTolerance": 10
}
```

### **Response Format**
```json
[
  {
    "question": "What is the chemical symbol for gold?",
    "options": ["Au", "Ag", "Fe", "Cu"],
    "correctAnswer": "Au",
    "explanation": "Au is the chemical symbol for gold",
    "isFromTemplate": true,
    "templateId": "template-123"
  },
  {
    "question": "What is the capital of France?",
    "options": ["London", "Paris", "Berlin", "Madrid"],
    "correctAnswer": "Paris",
    "explanation": "Paris is the capital of France",
    "isFromTemplate": false,
    "templateId": "new-template-456"
  }
]
```

## Database Queries

### **Finding Reusable Questions**
```sql
SELECT * FROM ai_question_templates
WHERE subject = 'Science'
  AND difficulty_score BETWEEN 40 AND 60  -- ±10 tolerance
  AND usage_count < 5                     -- Below max usage
  AND (last_used_at IS NULL OR 
       last_used_at < NOW() - INTERVAL '90 days')  -- Freshness check
ORDER BY usage_count ASC                   -- Least used first
LIMIT 2;                                   -- Max reuse count
```

### **Updating Usage Count**
```sql
UPDATE ai_question_templates
SET usage_count = usage_count + 1,
    last_used_at = NOW()
WHERE id = 'template-123';
```

## Benefits

### **🎯 Cost Reduction**
- **Reduced API Calls**: Reuse questions instead of generating new ones
- **Predictable Costs**: Control exactly how much AI generation is used
- **Efficient Resource Usage**: Balance between freshness and cost

### **🔄 Question Freshness**
- **Time-based TTL**: Questions automatically become "stale" after set period
- **Usage Limits**: Prevent overuse of popular questions
- **Difficulty Matching**: Ensure reused questions match current difficulty

### **⚙️ Flexible Configuration**
- **Per-Quiz Settings**: Different settings for different quiz types
- **Real-time Control**: Change settings without restarting
- **Granular Control**: Fine-tune every aspect of reuse behavior

## Best Practices

### **Recommended Settings by Use Case**

#### **High-Frequency Quizzes (Daily/Weekly)**
```typescript
{
  aiQuestionReuseEnabled: true,
  aiQuestionReusePercentage: 10,    // Low reuse for freshness
  aiQuestionFreshnessDays: 30,      // Shorter TTL
  aiQuestionMaxUsageCount: 3,       // Fewer reuses
  aiQuestionDifficultyTolerance: 5  // Tighter matching
}
```

#### **Occasional Quizzes (Monthly)**
```typescript
{
  aiQuestionReuseEnabled: true,
  aiQuestionReusePercentage: 30,    // Moderate reuse
  aiQuestionFreshnessDays: 90,      // Standard TTL
  aiQuestionMaxUsageCount: 5,       // Standard usage limit
  aiQuestionDifficultyTolerance: 10 // Standard tolerance
}
```

#### **Cost-Conscious Quizzes**
```typescript
{
  aiQuestionReuseEnabled: true,
  aiQuestionReusePercentage: 50,    // High reuse
  aiQuestionFreshnessDays: 180,     // Longer TTL
  aiQuestionMaxUsageCount: 10,      // More reuses
  aiQuestionDifficultyTolerance: 15 // Wider matching
}
```

### **Monitoring and Maintenance**

#### **Database Cleanup**
```sql
-- Remove very old unused questions
DELETE FROM ai_question_templates
WHERE created_at < NOW() - INTERVAL '1 year'
  AND usage_count = 0;

-- Archive heavily used questions
UPDATE ai_question_templates
SET usage_count = 0, last_used_at = NULL
WHERE usage_count >= 20;
```

#### **Performance Monitoring**
- Track API call reduction
- Monitor question freshness metrics
- Analyze reuse patterns by subject/difficulty

## Troubleshooting

### **Common Issues**

#### **No Questions Being Reused**
- Check if `aiQuestionReuseEnabled` is true
- Verify `aiQuestionReusePercentage` > 0
- Ensure database has questions for the subject
- Check if questions meet freshness criteria

#### **Too Many Questions Being Reused**
- Reduce `aiQuestionReusePercentage`
- Decrease `aiQuestionFreshnessDays`
- Lower `aiQuestionMaxUsageCount`

#### **Questions Too Repetitive**
- Increase `aiQuestionFreshnessDays`
- Lower `aiQuestionMaxUsageCount`
- Reduce `aiQuestionReusePercentage`

### **Debug Information**
The system logs detailed information about the reuse process:
```
🔄 Generating AI questions for: { subject: 'Science', difficulty: 50, questionCount: 10 }
📊 Looking for reusable questions with criteria: { maxReusedQuestions: 2, freshnessDate: '2024-01-01T00:00:00Z' }
✅ Reused 2 questions from database
🔄 Generating 8 new questions via AI
✅ Generated 8 new questions via AI
🎯 Final result: 10 questions (2 reused, 8 new)
```

## Future Enhancements

### **Planned Features**
- **Subject Clustering**: Group similar subjects for better reuse
- **Difficulty Learning**: Adapt difficulty matching based on usage patterns
- **Quality Scoring**: Rate question quality and prefer better questions
- **Bulk Operations**: Manage question templates in batches
- **Analytics Dashboard**: Visualize reuse patterns and effectiveness

### **Advanced Algorithms**
- **Smart Matching**: Use ML to find better question matches
- **Predictive Freshness**: Anticipate when questions will become stale
- **Dynamic Thresholds**: Adjust settings based on question availability 