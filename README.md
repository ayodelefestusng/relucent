# Relucent Clothing — Luxury Fashion E-Commerce Platform

A modern, enterprise-grade, mobile-first fashion e-commerce platform for **Relucent Clothing**, benchmarked against **Nui Chan (nuichan.com)**, **Zara**, and **H&M**.

## ✨ Features

- **Luxury Aesthetic**: Deep Onyx (`#111111`) and Champagne Gold (`#C9A865`) palette with `Playfair Display` serif typography and `Inter` sans-serif body copy.
- **Mobile-First UX**:
  - Sticky bottom purchase bar for one-handed mobile conversion.
  - Slide-over mini-cart drawer with real-time free shipping threshold tracker.
  - Swipeable multi-angle image lookbooks and zoom gallery.
- **Relucent FitFinder™ AI**: Interactive sizing engine estimating recommended size (*XS-XXL*) based on height, weight, category, and drape preference.
- **Multi-Currency Engine**: Instant toggle across NGN (`₦`), USD (`$`), GBP (`£`), and EUR (`€`).
- **Streamlined 1-Page Checkout**: Supporting guest checkout, auto-fill addresses, and live **Paystack**, **Flutterwave**, **Stripe (Apple Pay & Google Pay)**, and Direct Bank Transfer.
- **Global & Local Shipping**: Integrated with DHL Express Priority (Nigeria 1-2 days) and DHL Express Worldwide (3-5 business days).
- **VIP Patron Dashboard**: Order tracking, saved addresses, wishlist archives, and loyalty rewards tier system (*Silver, Gold, Platinum*).
- **Fast Tooling & Containerization**: Built with Astral `uv` and production-ready `Dockerfile` and `docker-compose.yml`.

---

## 🚀 Quick Start

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/ayodelefestusng/relucent.git
cd relucent

# Using Astral uv (recommended for ultra-fast setup):
uv sync
# Or using standard python venv:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r pyproject.toml
```

### 2. Configure Environment
Copy `.env.example` to `.env` and configure your credentials:
```bash
cp .env.example .env
```

### 3. Run Migrations & Seed Luxury Catalog Data
```bash
python manage.py migrate
python manage.py seed_relucent_data
```

### 4. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🛡️ Admin Portal
- **URL**: `http://127.0.0.1:8000/admin/`
- **Default Superuser**: `admin` / `relucent2026!`

---

## 🐳 Docker Deployment
```bash
docker compose up --build -d
```
