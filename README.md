# 🚚 Logistics SaaS Platform

Enterprise logistics cloud platform with AI-powered assistants for warehouse, transport, customer service, and management.

## Features

### 🏢 Four Main Modules

1. **Varastoapulainen (Warehouse Assistant)**
   - Inventory management
   - Task reminders and tracking
   - Anomaly detection
   - Priority suggestions

2. **Kuljetusapulainen (Transport Assistant)**
   - Route optimization
   - Delay risk detection
   - Load planning
   - Real-time tracking

3. **Asiakasapulainen (Customer Assistant)**
   - Message draft generation
   - Delay notifications
   - FAQ responses with templates
   - Customer communication management

4. **Johtoapulainen (Management Assistant)**
   - Key metrics dashboard
   - Anomaly alerts
   - Load forecasting
   - Analytics and reporting

## Tech Stack

- **Frontend:** React with TypeScript
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL
- **Hosting:** Microsoft Azure
- **Real-time:** WebSockets
- **Authentication:** JWT + OAuth2
- **APIs:** Google Maps, SendGrid, Twilio

## Project Structure

```
.
├── backend/              # Python FastAPI application
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   │   ├── warehouse/
│   │   │   ├── transport/
│   │   │   ├── customer/
│   │   │   ├── management/
│   │   │   └── auth/
│   │   ├── services/
│   │   ├── database/
│   │   └── utils/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/             # React TypeScript application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── modules/
│   │   │   ├── warehouse/
│   │   │   ├── transport/
│   │   │   ├── customer/
│   │   │   └── management/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── deploy.yml
└── docs/
    └── API.md
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+

### Local Development

```bash
# Clone repository
git clone https://github.com/jesuboi92-ai/logistics-saas.git
cd logistics-saas

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start with Docker Compose
docker-compose up -d

# Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Environment Variables

See `.env.example` files in backend and frontend directories.

## Contributing

1. Create feature branch from `develop`
2. Make changes
3. Submit PR for review

## License

MIT License - See LICENSE file
