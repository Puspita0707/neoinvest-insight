# 📈 NeoInvest Insight

NeoInvest Insight is an AI-powered **Investment Research and Learning Assistant** designed to help anyone understand the stock market — from **complete beginners to experienced retail investors**.

Instead of reading complex financial reports or searching multiple websites, users can simply **ask questions in natural language** and receive clear explanations, market insights, and research-backed responses.

It combines **AI reasoning, financial knowledge, and live information** to make stock market research **simpler, faster, and easier to understand**.

Users can learn how companies work, explore historical performance, compare stocks, understand investment strategies, and receive suggestions based on their **risk profile and financial goals**.

---

# Problem Statement

Many people want to invest in the stock market but face several challenges:

• Financial information is often **complex and difficult for beginners to understand**

• Market data is **scattered across multiple websites**

• Comparing companies requires significant research

• Beginners don't know **where to start or how to analyze a stock**

• Investment decisions are rarely aligned with **personal risk tolerance or budget**

As a result, new investors often feel overwhelmed and avoid investing altogether.

There is a need for a system that can **simplify financial knowledge, provide live insights, and guide users through investment decisions in a clear and intuitive way.**

---

# Solution

To address these challenges, I built **NeoInvest Insight**, an AI-powered assistant that helps users:

• Learn the basics of the stock market
• Understand companies and how they operate
• Compare different stocks before investing
• Get **latest market updates and insights**
• Receive **investment suggestions based on risk profile**
• Upload their own research documents for deeper analysis

NeoInvest Insight uses **Retrieval-Augmented Generation (RAG)** combined with **live information sources** to generate informative and structured responses.

The assistant acts as a **personal research companion** for anyone trying to understand or explore the stock market.

---

# What NeoInvest Insight Helps You Do

NeoInvest Insight allows users to:

• Learn **stock market fundamentals**
• Understand **how companies perform and grow over time**
• Analyze **historical trends and performance**
• Compare stocks for long-term investment
• Receive **risk-aware suggestions** based on investment style
• Explore **latest news and market updates**
• Upload research notes for personalized insights
• Save sessions and review previous research conversations

Whether you are **learning about stocks for the first time or researching a potential investment**, NeoInvest Insight helps you make **more informed decisions.**

---

# Example Questions You Can Ask

• Explain Reliance stock in simple terms
• Compare Apple and Microsoft for long-term investing
• Latest news about Tesla stock
• What does a balanced investor portfolio look like?
• Is Nvidia a good long-term investment?
• Explain stock market basics for beginners
• Which companies are strong in the semiconductor industry?

---

# Key Features

## 💬 Natural Language Stock Research

Users can ask financial questions in plain English and receive **structured and easy-to-understand explanations**.

---

## 🧠 Retrieval Augmented Generation (RAG)

NeoInvest Insight uses a curated **financial knowledge base** that includes:

• Indian and US market overview
• Beginner investing principles
• Risk profiles and allocation strategies
• Common investing mistakes

Documents are processed using **chunking and embeddings** to retrieve relevant information before generating answers.

---

## 🌐 Live Market Information

The assistant can optionally retrieve **recent market information** through:

• Tavily Web Search
• YouTube financial insights

This allows the system to provide **up-to-date context alongside financial explanations**.

---

## ⚙️ Personalized Investment Guidance

Users can customize responses based on:

**Response Mode**

* Concise
* Detailed

**Risk Profile**

* Conservative
* Balanced
* Aggressive

**Market Focus**

* India
* US
* Both

This helps align insights with the user's **investment style and goals**.

---

## 📂 Upload Research Notes

Users can upload research materials such as:

• TXT
• Markdown
• PDF
• DOCX

Uploaded content becomes part of the session context and can be referenced by the assistant.

---

## 👍 Feedback & Session Logging

NeoInvest Insight includes an evaluation mechanism:

• Thumbs-up / Thumbs-down feedback
• Saved chat sessions
• Feedback logs for future improvements

---

# Architecture

```
User Interface (Streamlit)
        │
        ▼
Chat Controller (app.py)
        │
        ▼
LLM Interface (models/llm.py)
        │
        ▼
Groq LLM (Llama-3.1-8B-Instant)
        │
        ├── RAG Retrieval
        │       └── utils/rag_utils.py
        │
        ├── Web Search
        │       └── utils/web_search.py
        │
        └── YouTube Search
                └── utils/youtube_search.py
```

---

# Project Structure

```
neoinvest-insight/
│
├── app.py
├── requirements.txt
│
├── config/
│   └── config.py
│
├── models/
│   └── llm.py
│
├── utils/
│   ├── rag_utils.py
│   ├── web_search.py
│   └── youtube_search.py
│
├── data/
│   └── knowledge/
│
└── logs/
```

---

# Tech Stack

**Frontend**

* Streamlit

**LLM Provider**

* Groq (Llama-3.1-8B-Instant)

**Embeddings**

* Sentence Transformers

**Retrieval System**

* Custom RAG pipeline

**Search Integration**

* Tavily API

**Document Processing**

* PyPDF
* python-docx

---

# Local Setup

Clone the repository:

```
git clone https://github.com/<your-username>/neoinvest-insight.git
cd neoinvest-insight
```

Create virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root:

```
LLM_PROVIDER=groq
GROQ_API_KEY=YOUR_GROQ_KEY

WEB_SEARCH_PROVIDER=tavily
TAVILY_API_KEY=YOUR_TAVILY_KEY
```

---

# Run the Application

```
streamlit run app.py
```

The application will start locally in your browser.

---

# Live Application

You can access the deployed application here:

```
https://neoinvest-insight-n7.streamlit.app
```

---

# Deployment

The app can be deployed using **Streamlit Cloud**.

Steps:

1. Push the repository to GitHub
2. Deploy using Streamlit Cloud
3. Add secrets in **App Settings → Secrets**

Example configuration:

```
LLM_PROVIDER="groq"
GROQ_API_KEY="YOUR_GROQ_KEY"

WEB_SEARCH_PROVIDER="tavily"
TAVILY_API_KEY="YOUR_TAVILY_KEY"
```

---
