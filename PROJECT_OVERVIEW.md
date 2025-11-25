# 📊 PromptSense - Project Overview

## 🎯 Project Goal

Improve LLM output quality by automatically personalizing prompts based on user context, history, and intent.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Browser)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         Modern Chat Interface (HTML/CSS/JS)          │   │
│  │  - User input                                        │   │
│  │  - Message display                                   │   │
│  │  - Real-time interactions                            │   │
│  │  - Analytics dashboard                               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/AJAX
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend (Python)                    │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Chat Routes  │  │History Routes│  │  API Routes  │      │
│  │              │  │              │  │              │      │
│  │ /api/chat    │  │ /api/history │  │ /api/health  │      │
│  │ /api/insights│  │ /api/user    │  │ /api/config  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Prompt Personalization Engine            │    │
│  │                                                     │    │
│  │  1. Detect Intent         [OpenAI Service]         │    │
│  │  2. Detect Domain         [OpenAI Service]         │    │
│  │  3. Get User Profile      [Database Service]       │    │
│  │  4. Get History           [Database Service]       │    │
│  │  5. Find Similar Queries  [FAISS Service]          │    │
│  │  6. Build Enhanced Prompt [Prompt Engine]          │    │
│  │  7. Generate Response     [OpenAI Service]         │    │
│  │  8. Save & Index          [DB + FAISS]             │    │
│  └────────────────────────────────────────────────────┘    │
│         │                  │                  │              │
│         ↓                  ↓                  ↓              │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐        │
│  │  OpenAI    │  │   Database   │  │    FAISS    │        │
│  │  Service   │  │   Service    │  │   Service   │        │
│  └────────────┘  └──────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
         │                  │                  │
         ↓                  ↓                  ↓
┌──────────────┐  ┌─────────────────┐  ┌──────────────┐
│  OpenAI API  │  │  Postgres Neon  │  │ Local Vector │
│              │  │   (Cloud DB)    │  │    Index     │
│  - GPT-4     │  │                 │  │              │
│  - Embeddings│  │  - Users        │  │  - 3072-dim  │
│              │  │  - Messages     │  │  - Metadata  │
└──────────────┘  └─────────────────┘  └──────────────┘
```

---

## 🔄 Data Flow

### User Sends Message

```
1. User types: "Explain blockchain"

2. Frontend sends to backend:
   POST /api/chat
   {
     "message": "Explain blockchain",
     "user_id": 1
   }

3. Backend processing:
   a) Get user profile from DB
      → User preferences: {tone: "friendly", level: "beginner"}

   b) Detect intent via OpenAI
      → "learning"

   c) Detect domain via OpenAI
      → "technology"

   d) Get recent conversation history
      → Last 5 messages from DB

   e) Generate embedding for query
      → OpenAI text-embedding-3-large
      → 3072-dimensional vector

   f) Search FAISS for similar queries
      → Finds: "crypto basics", "bitcoin explained"

   g) Build personalized prompt:
      [User Profile: beginner level, prefers friendly tone]
      [Detected Domain: technology, Intent: learning]
      [Similar queries: crypto basics, bitcoin explained]
      [Instructions: Explain in simple terms with examples]
      User Query: Explain blockchain

   h) Send enhanced prompt to OpenAI GPT-4

   i) Receive personalized response

   j) Save to database:
      - User message
      - Assistant response
      - Metadata (intent, domain)

   k) Add to FAISS index:
      - Embedding vector
      - Message metadata

4. Backend returns to frontend:
   {
     "success": true,
     "response": "Sure! Blockchain is like...",
     "metadata": {
       "intent": "learning",
       "domain": "technology",
       "similar_queries": [...]
     }
   }

5. Frontend displays response with metadata badges
```

---

## 🗄️ Database Schema

### Users Table
```sql
┌────┬────────────────────┬──────────────────────────────────┐
│ id │ email              │ preferences                      │
├────┼────────────────────┼──────────────────────────────────┤
│ 1  │ demo@prompt.ai     │ {tone: "friendly",               │
│    │                    │  level: "beginner",              │
│    │                    │  domains: ["tech", "coding"]}    │
├────┼────────────────────┼──────────────────────────────────┤
│ 2  │ advanced@prompt.ai │ {tone: "professional",           │
│    │                    │  level: "advanced",              │
│    │                    │  domains: ["finance", "data"]}   │
└────┴────────────────────┴──────────────────────────────────┘
```

### Messages Table
```sql
┌────┬─────────┬──────┬───────────────┬──────────┬──────────┐
│ id │ user_id │ role │ content       │ intent   │ domain   │
├────┼─────────┼──────┼───────────────┼──────────┼──────────┤
│ 1  │ 1       │ user │ Explain ML    │ learning │ tech     │
│ 2  │ 1       │ asst │ Machine learning...       │          │
│ 3  │ 1       │ user │ Tell me more  │ learning │ tech     │
└────┴─────────┴──────┴───────────────┴──────────┴──────────┘
```

---

## 🔍 FAISS Vector Search

### How It Works

```
Query: "What is neural network?"
   ↓
Generate Embedding
   ↓ [3072-dim vector]
   ↓
Search FAISS Index
   ↓
Find Top 3 Similar
   ↓
┌─────────────────────────────────────────┐
│ Similar Query 1: "Explain deep learning"│
│ Similarity: 0.89                        │
├─────────────────────────────────────────┤
│ Similar Query 2: "What is AI?"          │
│ Similarity: 0.78                        │
├─────────────────────────────────────────┤
│ Similar Query 3: "Machine learning?"    │
│ Similarity: 0.73                        │
└─────────────────────────────────────────┘
   ↓
Use as context for current query
```

---

## 🧮 Prompt Personalization Algorithm

```python
def build_personalized_prompt(user_msg, user_profile, intent,
                               domain, history, similar):
    prompt_parts = []

    # User context
    prompt_parts.append(
        f"[User: {user_profile.level}, {user_profile.tone}]"
    )

    # Intent & Domain
    prompt_parts.append(
        f"[Domain: {domain}, Intent: {intent}]"
    )

    # Similar queries
    if similar:
        prompt_parts.append(
            f"[Previously asked: {similar.join(', ')}]"
        )

    # Personalization rules
    if user_profile.level == "beginner":
        prompt_parts.append("[Use simple terms, add examples]")
    elif user_profile.level == "advanced":
        prompt_parts.append("[Provide technical depth]")

    if intent == "learning":
        prompt_parts.append("[Focus on education]")
    elif intent == "problem_solving":
        prompt_parts.append("[Provide actionable steps]")

    # Add user message
    prompt_parts.append(f"\nUser: {user_msg}")

    return "\n".join(prompt_parts)
```

---

## 📈 Key Metrics

### System Performance
- **Average Response Time**: < 3 seconds
- **Context Accuracy**: Uses last 5 conversations
- **Similar Query Matching**: Top 3 most relevant
- **Vector Dimension**: 3072 (OpenAI text-embedding-3-large)

### Personalization Factors
1. **User Expertise**: Beginner, Intermediate, Advanced
2. **Communication Tone**: Friendly, Professional, Casual
3. **Intent Categories**: 6 types (learning, problem-solving, creative, etc.)
4. **Domain Categories**: 8 types (tech, science, business, etc.)

---

## 🎨 Frontend Features

### Chat Interface
- Modern dark theme
- Smooth animations
- Real-time typing indicators
- Message history
- User switching

### Analytics Dashboard
- Total messages count
- Indexed queries (FAISS)
- Common domains
- Intent distribution
- User insights

---

## 🔐 Security Considerations

- API keys stored in environment variables
- Database credentials not committed to repo
- SQL injection prevention (parameterized queries)
- Input validation on all endpoints
- CORS enabled for frontend

---

## 🚀 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Flask (Python) | Web framework |
| LLM | OpenAI GPT-4o-mini | Response generation |
| Embeddings | OpenAI text-embedding-3-large | Vector generation |
| Vector DB | FAISS | Similarity search |
| Database | Postgres Neon | Cloud database |
| Frontend | HTML/CSS/JS | User interface |
| Styling | Custom CSS | Modern dark theme |

---

## 📝 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/chat | Send message, get response |
| GET | /api/history/{user_id} | Get message history |
| GET | /api/chat/insights/{user_id} | Get user analytics |
| GET | /api/user/{user_id} | Get user profile |
| GET | /api/users | Get all users |
| GET | /api/health | Health check |
| GET | /api/config | Get configuration |

---

## 🎓 Academic Value

### Problem Statement
Generic LLM prompts lead to:
- Inconsistent response quality
- Lack of user-specific adaptation
- No learning from interaction history
- Manual prompt engineering burden

### Solution: PromptSense
Automatically enhances prompts with:
- User profile context
- Conversation history
- Similar query patterns
- Intent-driven instructions
- Domain-specific guidance

### Innovation
1. **Context Integration**: Combines multiple context sources
2. **Vector Search**: Uses embeddings for query similarity
3. **Adaptive Personalization**: Learns from user patterns
4. **Real-time Enhancement**: Instant prompt optimization

### Evaluation Metrics
- Response relevance (subjective rating)
- Context utilization rate
- Query resolution success
- User satisfaction score
- Similar query match accuracy

---

## 🔮 Future Enhancements

### Phase 1 (Immediate)
- [ ] User authentication
- [ ] Session management
- [ ] Export chat history

### Phase 2 (Short-term)
- [ ] Prompt template library
- [ ] A/B testing framework
- [ ] Response quality feedback
- [ ] Multi-language support

### Phase 3 (Long-term)
- [ ] Fine-tuned models
- [ ] Custom embedding models
- [ ] Advanced analytics
- [ ] Mobile application

---

## 📊 Performance Optimization

### Current Optimizations
- Lazy loading of services
- Connection pooling for database
- FAISS index caching
- Batch embedding generation

### Scalability Considerations
- Horizontal scaling with load balancer
- Redis cache for frequent queries
- Async processing for embeddings
- CDN for static assets

---

## 🏆 Project Achievements

✅ Full-stack implementation
✅ Production-ready code
✅ Modern UI/UX
✅ Vector similarity search
✅ Cloud database integration
✅ Comprehensive documentation
✅ Easy setup process
✅ Demo-ready application

---

## 📞 Presentation Talking Points

1. **Problem**: Generic prompts = inconsistent results
2. **Solution**: Automatic context-aware personalization
3. **Demo**: Show before/after prompt enhancement
4. **Tech**: Flask + OpenAI + FAISS + Postgres
5. **Results**: More relevant, personalized responses
6. **Innovation**: Combines user profile, history, and vector search

---

**This document provides a comprehensive overview for understanding, presenting, and extending the PromptSense system.**
