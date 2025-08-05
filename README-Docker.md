# Elective Management System - Docker Setup

This Django application helps manage student elective subject allocations.

## Quick Start with Docker

### Development Mode

1. **Build and run the application:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Web interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin/

3. **Create a superuser (in a new terminal):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Production Mode

1. **Build the production image:**
   ```bash
   docker build -f Dockerfile.prod -t elective-management-system:prod .
   ```

2. **Run the production container:**
   ```bash
   docker run -d \
     --name elective-management-prod \
     -p 8000:8000 \
     -v elective_static:/app/staticfiles \
     -v elective_media:/app/media \
     -v elective_db:/app/db \
     elective-management-system:prod
   ```

## Docker Commands

### Development
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Access shell
docker-compose exec web bash

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Production
```bash
# Build production image
docker build -f Dockerfile.prod -t elective-management-system:prod .

# Run production container
docker run -d \
  --name elective-management-prod \
  -p 8000:8000 \
  -e DEBUG=0 \
  -e SECRET_KEY=your-secret-key-here \
  -e ALLOWED_HOSTS=your-domain.com \
  elective-management-system:prod

# View container logs
docker logs elective-management-prod

# Access container shell
docker exec -it elective-management-prod bash
```

## Environment Variables

- `DEBUG`: Set to 0 for production
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DJANGO_SETTINGS_MODULE`: Django settings module (default: PMS.settings)

## Volumes

- `/app/staticfiles`: Static files
- `/app/media`: Media files
- `/app/db`: Database files (SQLite)
- `/app/logs`: Application logs

## Features

- **Masters Student Support**: Special allocation logic for Masters students
- **Subject Capacity Management**: Configurable min/max students per subject
- **Priority-based Allocation**: Students can prioritize their elective choices
- **Admin Interface**: Full Django admin for managing subjects, students, and batches
- **Excel Export**: Generate reports in Excel format

## Health Check

The containers include health checks that verify the application is responding correctly.

## Troubleshooting

1. **Port already in use**: Change the port mapping in docker-compose.yml
2. **Permission issues**: Ensure proper file permissions on mounted volumes
3. **Database issues**: Check if migrations need to be run
4. **Static files not loading**: Run `collectstatic` command
