# Django E-Commerce API

A comprehensive RESTful API for Django-based e-commerce applications with product management, user authentication, order processing, and payment integration features.

## Features

- **Product Management**: Create, update, list, and delete products
- **User Authentication**: Secure JWT-based authentication via djangorestframework-simplejwt
- **Order Processing**: Complete order workflow management
- **Payment Integration**: Stripe payment processing
- **RESTful API**: Well-structured API endpoints for all e-commerce operations

## Technology Stack

- Python (3.6-3.9)
- Django 3.2+
- Django REST Framework
- PostgreSQL (recommended) or SQLite for development SQLite for development
- JWT Authentication
- Stripe for payment processing

## Installation

### Prerequisites

- Python 3.6-3.9
- pip or uv package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/berkaykrc/django-ecommerce-api.git
   cd django-ecommerce-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   
   **Option 1: Simple approach for standalone application**
   ```bash
   using uv
   uv install
   ```
   
   **Option 2: Package approach (if you want to reuse the apps elsewhere)**
   ```bash
   # Using pip with editable mode
   pip install -e .
   pip install -e ".[dev]"  # Include development dependencies
   
   # Or using uv
   uv install -e .
   uv install -e . --dev
   ```

4. Configure environment variables:
   ```bash
   cp ecommerce_django/ecommerce_django/.env.dist ecommerce_django/ecommerce_django/.env
   # Edit the .env file with your settings
   ```

5. Run migrations:
   ```bash
   cd ecommerce_django
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication

- `POST /api/auth/jwt/create/`: Obtain JWT token
- `POST /api/auth/jwt/refresh/`: Refresh JWT token
- `POST /api/auth/users/`: Register a new user

### Products

- `GET /api/products/`: List all products
- `POST /api/products/`: Create a new product
- `GET /api/products/{id}/`: Retrieve a specific product
- `PUT /api/products/{id}/`: Update a product
- `DELETE /api/products/{id}/`: Delete a product

### Orders

- `GET /api/orders/`: List user orders
- `POST /api/orders/`: Create a new order
- `GET /api/orders/{id}/`: Retrieve order details
- `POST /api/orders/{id}/checkout/`: Process payment for an order

## Development

### Dependencies

This project uses `uv` for dependency management. The `uv.lock` file ensures consistent installations across environments and should be committed to version control.

To update dependencies:
```bash
uv pip install <package>  # Add a new dependency
uv pip install <package> --dev  # Add a development dependency
```

### Code Quality

The project uses Ruff for linting and formatting:

```bash
ruff check .
ruff format .
```

### Testing

Run tests with pytest:

```bash
pytest
```

## Payment Integration

This project integrates with Stripe for payment processing. To use Stripe:

1. Sign up for a Stripe account and get your API keys
2. Add your Stripe API keys to the `.env` file
3. Use the checkout endpoints to process payments

## License

[MIT License](LICENSE)
