# Running the Elective Management System Locally

This guide shows you how to run the Django Elective Management System on your local device using either Docker or directly with Python.

## ✅ System Status

- **Docker Images**: Built and tested successfully
- **Development & Production**: Both configurations working
- **Database**: SQLite for development, PostgreSQL for production
- **Issues Fixed**: All Docker build and container issues resolved

## 🐳 Method 1: Using Docker (Recommended)

### Prerequisites
- Docker installed on your system
- At least 2GB free disk space

### Development Mode (Fastest for testing)

```bash
# 1. Navigate to the project directory
cd /home/abhiyan/Elective-Management-System-1

# 2. Build the development Docker image
docker build -t elective-system-dev .

# 3. Run the development container
docker run -d --name elective-dev -p 8000:8000 elective-system-dev

# 4. Access the application
# Open your browser and go to: http://localhost:8000
```

### Production Mode (More realistic deployment)

```bash
# 1. Navigate to the project directory
cd /home/abhiyan/Elective-Management-System-1

# 2. Build the production Docker image
docker build -f Dockerfile.prod -t elective-system-prod .

# 3. Run the production container
docker run -d --name elective-prod -p 8000:8000 elective-system-prod

# 4. Access the application
# Open your browser and go to: http://localhost:8000
# Note: Production mode redirects HTTP to HTTPS, so you might see a redirect notice
```

### Docker Compose (Complete setup with database)

```bash
# 1. Start all services
docker-compose up -d

# 2. Access the application
# Open your browser and go to: http://localhost:8000

# 3. Stop all services
docker-compose down
```

## 🐍 Method 2: Running Directly with Python

### Prerequisites
- Python 3.11+ installed
- pip package manager

### Setup Steps

```bash
# 1. Navigate to the project directory
cd /home/abhiyan/Elective-Management-System-1/PMS

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Create a superuser account
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic

# 7. Start the development server
python manage.py runserver

# 8. Access the application
# Open your browser and go to: http://localhost:8000
```

## 🔐 Default Login Credentials

When using Docker, the system creates a default admin account:
- **Username**: admin
- **Password**: adminpassword123
- **Email**: admin@example.com

When running with Python directly, you'll create your own superuser account in step 5.

## 📱 Accessing the System

### Main URLs
- **Home Page**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Student Portal**: http://localhost:8000/student/
- **Course Management**: http://localhost:8000/course/

### Key Features
1. **Admin Panel**: Manage users, courses, and elective subjects
2. **Student Registration**: Students can register and set elective priorities
3. **Algorithm Execution**: Run allocation algorithms (1-5 subjects for Masters, 2 for Bachelors)
4. **Excel Export**: Download allocation results as Excel files
5. **PDF Reports**: Generate PDF reports for results

## 🛠️ Useful Docker Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View container logs
docker logs <container-name>

# Stop a container
docker stop <container-name>

# Remove a container
docker rm <container-name>

# View Docker images
docker images

# Remove unused images
docker image prune
```

## 🔧 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Use a different port
   docker run -d --name elective-dev -p 8001:8000 elective-system-dev
   # Then access: http://localhost:8001
   ```

2. **Permission denied errors**
   ```bash
   # Make sure you have proper permissions
   sudo docker run -d --name elective-dev -p 8000:8000 elective-system-dev
   ```

3. **Database issues in Python mode**
   ```bash
   # Reset the database
   rm pms_db.sqlite3
   python manage.py migrate
   python manage.py createsuperuser
   ```

## 📊 System Architecture

- **Backend**: Django 4.x with Python 3.11
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Django templates with Bootstrap
- **Static Files**: Handled by WhiteNoise in production
- **Algorithm**: Custom allocation algorithm for elective subjects
- **Export**: openpyxl for Excel, ReportLab for PDF

## 🚀 Next Steps

1. **Access the admin panel** and set up courses and elective subjects
2. **Configure academic levels** (Bachelor's/Master's programs)
3. **Add elective subjects** with capacity limits
4. **Test student registration** and priority setting
5. **Run the allocation algorithm** to see results

The system is now fully functional and ready for use! 🎉
