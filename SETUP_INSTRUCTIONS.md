# PromptSense Setup Instructions

## ✅ Completed Steps

1. ✅ Created `.env` file
2. ✅ Created Python virtual environment (`venv/`)
3. ✅ Installed all Python dependencies

## 🔧 Next Steps - REQUIRED

### Step 1: Configure Your API Keys

Edit the `.env` file and replace the placeholder values:

#### A. OpenAI API Key (REQUIRED)
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

**Where to get it:**
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Paste it in `.env`

#### B. Postgres Neon Database (REQUIRED)
```env
DATABASE_URL=postgresql://username:password@host.neon.tech/dbname?sslmode=require
```

**Where to get it:**
1. Go to https://neon.tech
2. Sign up for free account
3. Create a new project
4. Copy the connection string from the dashboard
5. Paste it in `.env`

### Step 2: Initialize the Database

Once you've configured the DATABASE_URL, run:

```bash
venv\Scripts\python.exe init_db.py
```

This will:
- Create the `users` and `messages` tables
- Insert 2 demo users (Beginner and Advanced)

### Step 3: Start the Application

```bash
venv\Scripts\python.exe app.py
```

The server will start on http://localhost:5000

### Step 4: Test in Browser

Open: http://localhost:5000

You should see the PromptSense chat interface.

---

## 🚨 Troubleshooting

### Error: "OPENAI_API_KEY not set"
- Make sure you saved the `.env` file after editing
- Check that the key starts with `sk-`
- Restart the Flask server

### Error: "Could not connect to database"
- Verify your DATABASE_URL is correct
- Check that Neon.tech database is accessible
- Make sure the connection string includes `?sslmode=require`

### Error: "Module not found"
- Make sure you're using the virtual environment:
  ```bash
  venv\Scripts\python.exe app.py
  ```
  NOT just `python app.py`

---

## 📁 Project Structure Overview

```
Gen AI project/
├── app.py                 # Main Flask application (START HERE)
├── config.py              # Configuration from .env
├── .env                   # Your secrets (FILL THIS IN)
├── requirements.txt       # Python dependencies (INSTALLED ✅)
├── init_db.py            # Database setup script
├── venv/                  # Virtual environment (CREATED ✅)
├── models/
│   └── schema.sql        # Database schema
├── services/
│   ├── prompt_engine.py  # Core AI logic
│   ├── openai_service.py # OpenAI API calls
│   ├── faiss_service.py  # Vector search
│   └── db_service.py     # Database operations
├── routes/
│   ├── chat.py           # Chat API endpoints
│   └── history.py        # History API endpoints
├── templates/
│   └── index.html        # Frontend UI
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## 🎯 Quick Start Commands

```bash
# Activate virtual environment (if needed)
venv\Scripts\activate

# Initialize database (after configuring .env)
python init_db.py

# Start the server
python app.py

# Access the app
# Open browser: http://localhost:5000
```

---

## 💡 Tips

1. **Cost Control**: This app uses OpenAI API. Each chat costs ~$0.01-0.05. Monitor usage at https://platform.openai.com/usage

2. **Demo Users**: The app comes with 2 pre-configured users:
   - User 1: Beginner level, friendly tone
   - User 2: Advanced level, professional tone

3. **FAISS Index**: First-time use creates `faiss_index.bin` and `faiss_metadata.json` - these store your query embeddings locally

---

## 📊 What Happens When You Send a Message

1. Your message → Flask API
2. OpenAI detects **intent** (learning, problem-solving, creative, etc.)
3. OpenAI detects **domain** (technology, science, business, etc.)
4. OpenAI generates **embedding** (3072-dim vector)
5. FAISS searches for **similar past queries**
6. System builds **enhanced prompt** with:
   - User profile (expertise level, tone preference)
   - Detected intent and domain
   - Similar past queries
   - Recent conversation history
7. Enhanced prompt → OpenAI → Personalized response
8. Response shown to you + metadata (intent, domain, similar queries)

---

**Ready to continue? Once you've configured your API keys in `.env`, let me know!**
