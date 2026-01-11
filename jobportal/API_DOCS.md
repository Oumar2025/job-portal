# API Documentation

## Authentication
POST /api/token/ - Get JWT token
POST /api/token/refresh/ - Refresh token

## Jobs
GET /api/jobs/ - List all jobs (public)
GET /api/jobs/{id}/ - Job details (authenticated)
POST /api/jobs/{id}/apply/ - Apply for job (authenticated)

## User
GET /api/my-applications/ - User's applications