# Logistics SaaS Platform - Development Guide

## Project Structure

```
logistics-saas/
├── backend/              # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic validation schemas
│   │   ├── api/          # API route handlers
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities and helpers
│   ├── requirements.txt
│   ├── Dockerfile
│   └── scripts/          # Database initialization
├── frontend/             # React TypeScript Frontend
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── stores/       # Zustand state management
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.ts
├── docker-compose.yml    # Local development setup
└── .github/workflows/    # CI/CD pipelines
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/jesuboi92-ai/logistics-saas.git
cd logistics-saas

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec backend python scripts/init_db.py
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### Default Credentials

```
Email: admin@logistics.com
Password: admin123
```

## Development Workflow

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/
isort app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

## API Documentation

### Authentication

#### Register User
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "password": "secure_password"
}
```

#### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

### Warehouse Module

#### Get Tasks
```bash
GET /api/v1/warehouse/tasks?status=pending&priority=high
Authorization: Bearer {access_token}
```

#### Create Task
```bash
POST /api/v1/warehouse/tasks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "task_type": "picking",
  "description": "Pick items for order #001",
  "priority": "high",
  "due_date": "2024-01-15T18:00:00"
}
```

#### Detect Anomalies
```bash
GET /api/v1/warehouse/anomalies
Authorization: Bearer {access_token}
```

### Transport Module

#### Get Shipments
```bash
GET /api/v1/transport/shipments?status=in_transit
Authorization: Bearer {access_token}
```

#### Create Shipment
```bash
POST /api/v1/transport/shipments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "shipment_number": "SHIP-20240115-ABC123",
  "order_id": "uuid",
  "vehicle_id": "uuid",
  "weight_kg": 25.5,
  "scheduled_delivery": "2024-01-16T18:00:00"
}
```

#### Get Shipment Tracking
```bash
GET /api/v1/transport/shipments/{shipment_id}/tracking
Authorization: Bearer {access_token}
```

#### Check Delay Risk
```bash
POST /api/v1/transport/shipments/{shipment_id}/check-delay-risk
Authorization: Bearer {access_token}
```

### Customer Module

#### Get Customers
```bash
GET /api/v1/customer/customers
Authorization: Bearer {access_token}
```

#### Create Customer
```bash
POST /api/v1/customer/customers
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "customer_name": "Company Name",
  "email": "contact@company.com",
  "phone": "+1234567890",
  "address": "123 Street",
  "city": "City",
  "postal_code": "12345",
  "country": "Country"
}
```

#### Get Orders
```bash
GET /api/v1/customer/orders?status=pending
Authorization: Bearer {access_token}
```

#### Create Order
```bash
POST /api/v1/customer/orders
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "order_number": "ORD-20240115-ABC",
  "customer_id": "uuid",
  "total_amount": 599.99,
  "items": [
    {"sku": "SKU001", "quantity": 5, "price": 99.99}
  ],
  "delivery_address": "123 Delivery Street"
}
```

#### Draft Communication
```bash
POST /api/v1/customer/communications/draft
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "customer_id": "uuid",
  "communication_type": "notification",
  "message_body": "Your order is on the way",
  "recipient": "customer@example.com"
}
```

### Management Module

#### Get Dashboard
```bash
GET /api/v1/management/dashboard
Authorization: Bearer {access_token}
```

#### Get Metrics
```bash
GET /api/v1/management/metrics?category=warehouse&period=daily
Authorization: Bearer {access_token}
```

#### Get Anomalies
```bash
GET /api/v1/management/anomalies?severity=critical&status=open
Authorization: Bearer {access_token}
```

#### Get Forecasts
```bash
GET /api/v1/management/forecasts?forecast_type=demand
Authorization: Bearer {access_token}
```

#### Generate Forecast
```bash
POST /api/v1/management/forecasts/generate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "forecast_type": "demand",
  "target_metric": "order_volume",
  "days_ahead": 7
}
```

#### Generate Report
```bash
POST /api/v1/management/reports/generate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "report_type": "daily",
  "include_metrics": ["warehouse_utilization", "shipment_performance"]
}
```

## Database Schema

### Tables
- `users` - User accounts and authentication
- `inventory` - Warehouse inventory items
- `stock_movements` - Stock transaction history
- `warehouse_items` - Physical inventory items
- `warehouse_tasks` - Warehouse work tasks
- `vehicles` - Transport vehicles
- `routes` - Delivery routes
- `shipments` - Shipment records
- `shipment_tracking` - Real-time GPS tracking
- `customers` - Customer information
- `customer_orders` - Customer orders
- `communications` - Customer communications
- `message_templates` - Message templates
- `dashboard_metrics` - KPI metrics
- `anomalies` - Detected anomalies
- `forecasts` - Demand/load forecasts
- `reports` - Generated reports

## Testing

### Run All Tests
```bash
cd backend
pytest -v
```

### Run Specific Test
```bash
pytest tests/test_warehouse.py::test_create_task -v
```

### Coverage Report
```bash
pytest --cov=app --cov-report=html
```

## Deployment

### Azure Deployment

Requirements:
- Azure Container Registry
- Azure App Service
- Azure Database for PostgreSQL

Environment Variables:
```
ACR_LOGIN_SERVER=your-acr.azurecr.io
ACR_USERNAME=your-username
ACR_PASSWORD=your-password
AZURE_PUBLISH_PROFILE=your-publish-profile
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Docker Compose Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Rebuild
docker-compose down -v
docker-compose up -d
```

### API Connection Issues
```bash
# Check backend is running
docker-compose ps backend

# View logs
docker-compose logs backend

# Verify API
curl http://localhost:8000/health
```

## Contributing

1. Create feature branch: `git checkout -b feature/feature-name`
2. Make changes and commit: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/feature-name`
4. Submit pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions, please create an issue in the GitHub repository.
