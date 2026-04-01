# 📚 Smart Book Recommendation System for books

A **web app** that recommends books based on user behavior and book content.  
Built with **Flask**, **Python**, and **scikit-learn**, using a **hybrid approach** (TF‑IDF + collaborative filtering).

---

## 🚀 Features

- 🔐 User registration, login, and secure sessions
- 🎯 Personalized recommendations (hybrid ML engine)
- 🔍 Search by title + filter by genre
- 📖 Book detail pages with metadata and content
- ❤️ Favorites: add/remove books per user
- ☁️ Deployed on **Vercel**

---

## 🧠 Tech Stack

- **Backend:** Python 3.x, Flask 3.0.3, Werkzeug, scikit-learn, pandas, numpy, sqlite3
- **Frontend:** HTML5, CSS3, JavaScript, Jinja2
- **Data:** CSV files (`books.csv`, ratings/interaction data)
- **Deployment:** Vercel (`@vercel/python`, `vercel.json`)

---

## 🧮 Recommendation Logic

- **Content-based:** TF‑IDF on book descriptions/genres + cosine similarity  
- **Collaborative filtering:** Uses user–book interactions  
- **Hybrid:** Combines both scores to produce Top‑N recommendations

---

## 📁 Project Structure

```bash
Smart-Recommendation-System/
├── app.py
├── requirements.txt
├── vercel.json
├── data/
│   └── books.csv
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── book_detail.html
│   └── favourites.html
└── static/
    ├── style.css
    └── script.js
```
---

## 🛠️ Setup

```bash
git clone https://github.com/<your-username>/Smart-Recommendation-System.git
cd Smart-Recommendation-System

python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
flask run   # or: python app.py
```

Open: `http://127.0.0.1:5000`

---

## 🔮 Future Work

- BERT-based embeddings for better text understanding  
- Real-time updates (WebSockets)  
- Advanced recommender algorithms (matrix factorization, Neural CF)  
- Mobile app + social features

---

