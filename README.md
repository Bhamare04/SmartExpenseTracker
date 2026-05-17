# Smart Expense Tracker with Financial Insights

A resume-ready full-stack expense tracker built with HTML5, CSS3, JavaScript, Python, Django, and MySQL.

## Features

- User registration, login, logout, and forgot-password flow
- Dashboard with income, expense, balance, savings, and budget status
- Income and expense management with edit/delete/search/filter
- Monthly budget management with warnings and progress bar
- Analytics charts for categories, monthly activity, and savings trends
- Smart category suggestions and financial insights
- CSV and PDF report export
- Profile update, password change, and image upload
- Admin panel for reviewing users and records

## Folder Structure

- `smart_expense_tracker/` - Django project settings and root routing
- `tracker/` - Main application with models, forms, views, utilities, and admin setup
- `templates/` - Shared templates and page templates
- `static/` - CSS and JavaScript assets

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create a MySQL database, for example `smart_expense_tracker`.
4. Set environment variables if needed:

   - `MYSQL_DATABASE`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_HOST`
   - `MYSQL_PORT`

5. Run migrations:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

7. Seed demo data (optional):

   ```bash
   python manage.py seed_demo_data
   ```

8. Start the development server:

   ```bash
   python manage.py runserver
   ```

## Free Deployment Guide: Render + Railway MySQL

This project can be deployed for free using:

- Render for the web app
- Railway for the MySQL database

### 1. Prepare the project

Make sure these files exist in the project root:

- `requirements.txt`
- `Procfile`
- `runtime.txt`

Make sure the project already includes these deployment settings:

- `gunicorn`
- `whitenoise`
- MySQL configuration in `smart_expense_tracker/settings.py`

### 2. Install the required packages locally

Run this in your terminal:

```bash
python -m pip install -r requirements.txt
```

### 3. Run migrations locally

If you are testing before deployment, run:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Collect static files locally

Run:

```bash
python manage.py collectstatic --noinput
```

### 5. Push the project to GitHub

Use these Git commands if your project is not on GitHub yet:

```bash
git init
git add .
git commit -m "Prepare for deployment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 6. Create the Railway MySQL database

1. Sign in to Railway.
2. Create a new project.
3. Add a MySQL database plugin.
4. Open the database settings.
5. Copy these values:
   - database name
   - username
   - password
   - host
   - port

### 7. Create the Render web service

1. Sign in to Render.
2. Create a new Web Service.
3. Connect your GitHub repository.
4. Select this project.
5. Set the build command:

```bash
pip install -r requirements.txt
```

6. Set the start command:

```bash
gunicorn smart_expense_tracker.wsgi:application
```

### 8. Set environment variables on Render

Add these variables in the Render dashboard:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=<your-render-service-name>.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://<your-render-service-name>.onrender.com`
- `MYSQLDATABASE=<Railway database name>`
- `MYSQLUSER=<Railway username>`
- `MYSQLPASSWORD=<Railway password>`
- `MYSQLHOST=<Railway host>`
- `MYSQLPORT=<Railway port>`

If Render gives you `RENDER_EXTERNAL_HOSTNAME` and `RENDER_EXTERNAL_URL`, the project will use them automatically.

For a local reference, copy the values from [.env.example](.env.example) and replace the placeholders with your own production values.

### 9. Deploy and run migrations on Render

After Render finishes building, open the Render shell and run:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 10. Test the live app

Open your Render URL and check:

- homepage
- login page
- dashboard
- expense and income forms
- static files like CSS and JavaScript

## Deployment Files

### Procfile

Use this exact content:

```bash
web: gunicorn smart_expense_tracker.wsgi:application
```

### runtime.txt

Use this exact content:

```bash
python-3.12.8
```

### MySQL settings

The project reads Railway-style MySQL environment variables in `settings.py`. The database is used automatically when `MYSQLDATABASE` is present.

## Common Errors and Fixes

### 1. DisallowedHost error

Add your Render domain to `ALLOWED_HOSTS`.

### 2. CSRF verification failed

Add your Render URL to `CSRF_TRUSTED_ORIGINS`.

### 3. Static files not loading

Make sure `whitenoise` is installed and `python manage.py collectstatic --noinput` has been run.

### 4. MySQL connection failed

Check the Railway values for database name, username, password, host, and port.

### 5. App starts but shows a 500 error

Check the Render logs and confirm all environment variables are set correctly.

## Final Deployment Checklist

- GitHub repository pushed
- Railway MySQL database created
- Render web service created
- Environment variables set
- `migrate` run on Render
- `createsuperuser` run on Render
- `collectstatic --noinput` run on Render
- App opens without errors

## Quick Copy-Paste Order

Use this order when you deploy:

1. Push the project to GitHub.
2. Create the Railway MySQL database.
3. Create the Render web service.
4. Set the Render environment variables.
5. Deploy the app on Render.
6. Run these commands in the Render shell:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

7. Open the live site and test login, dashboard, and static files.

## URLs

- `/` Home
- `/register/` Registration
- `/login/` Login
- `/dashboard/` Main dashboard
- `/income/` Income management
- `/expenses/` Expense management
- `/budget/` Budget management
- `/reports/` Analytics and export
- `/profile/` Profile settings
- `/admin-panel/` Superuser panel
- `/forgot-password/` Forgot password page

## Database Design

The application uses Django ORM models for:

- `User` from Django authentication
- `Profile`
- `Income`
- `Expense`
- `Budget`

## Notes

- MySQL is configured in `settings.py`.
- Password reset uses Django's built-in auth flow with console email backend for development.
- Reports are rendered with Chart.js and exported through Django views.
