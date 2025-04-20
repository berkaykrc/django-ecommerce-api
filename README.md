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
   or
   uv venv  # Using uv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   using uv
   uv sync
   ```

4. Configure environment variables:
   ```bash
   cp ecommerce_django/ecommerce_django/.env.dist ecommerce_django/ecommerce_django/.env
   # Edit the .env file with your credentials and settings
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

- `GET /api/v1/products/latest-products/`: List all products
- `GET /api//v1/products/<category_slug>/<product_slug>/`: finds a product based on both its category slug and product slug.
- `POST /api/v1/products/product/search/`: search products by name
- `GET /api/v1/product/<category_slug>/`: Retrieve information about a specific category

### Orders

- `GET /api/v1/orders/`: List user orders
- `POST /api/v1/orders/checkout/`: Process payment for an order and create a new order

## Development

### Dependencies

This project uses `uv` for dependency management. The `uv.lock` file ensures consistent installations across environments and should be committed to version control.

To update dependencies:
```bash
uv add <package>  # Add a new dependency
uv add <package> --dev  # Add a development dependency
```

### Code Quality

The project uses Ruff for linting and formatting:

```bash
uv run ruff check .
uv run ruff format .
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
