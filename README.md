# VIP-Cards
VIP Wedding Planner Card Web App with QR Codes, Loyalty Points &amp; Competitions
VIP Project is a web application built with **Python** and **Flask**, containerized with **Docker** for easy development and deployment.

### Features
- Run the app in Docker containers.
- PostgreSQL database support.
- Database migrations using Alembic.
- Gunicorn configuration for production deployment.
- Organized project structure for maintainability.

### Requirements
- Python 3.10+
- Docker & Docker Compose
- Git

### Installation & Running
1. Clone the repository:
```bash
git clone https://github.com/username/VIP.git
cd VIP
Create a virtual environment and install dependencies:

bash
Copy code
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
Run the application using Docker Compose:

bash
Copy code
docker-compose up --build
Configuration
Database settings are in config.py.

Docker and Docker Compose files simplify local or server deployment.

Contribution
Contributions are welcome! Open an issue or submit a pull request.

License
MIT License
