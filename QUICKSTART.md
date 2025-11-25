# ⚡ Quick Start Guide

Get PromptSense running in 5 minutes!

## 📋 Checklist

Before you start, make sure you have:
- [ ] Python 3.9+ installed
- [ ] OpenAI API key
- [ ] Postgres Neon database (free tier works!)

---

## 🚀 Setup Steps

### 1️⃣ Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2️⃣ Get Your API Keys

**OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

**Postgres Neon Database:**
1. Go to https://neon.tech
2. Sign up (free)
3. Create a new project
4. Copy the connection string from the dashboard

### 3️⃣ Configure Environment

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname
```

### 4️⃣ Initialize Database

```bash
python init_db.py
```

Type `y` when prompted.

### 5️⃣ Run the Application

```bash
python app.py
```

### 6️⃣ Open in Browser

```
http://localhost:5000
```

---

## 🎉 You're Ready!

Try these example queries:
- "Explain machine learning"
- "How does blockchain work?"
- "What is Python?"
- "Teach me about neural networks"

Switch between users to see how responses adapt!

---

## 🆘 Having Issues?

### Python not found
Install from https://python.org

### Module errors
Make sure virtual environment is activated:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### Database connection error
Check your `DATABASE_URL` in `.env`

### OpenAI API error
Verify your `OPENAI_API_KEY` in `.env`

---

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints
- Customize user preferences
- Check out the insights dashboard

---

**Need more help?** Check README.md or create an issue!
