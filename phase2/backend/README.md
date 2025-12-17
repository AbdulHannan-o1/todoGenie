# TodoGenie Backend

This is the backend for the TodoGenie application. It is a FastAPI application that provides a RESTful API for managing tasks.

## Setup

To set up the backend for development, follow these steps:

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up the database:**

    The backend uses Neon Serverless PostgreSQL database as required for Phase 2 of the hackathon. Sign up at [neon.tech](https://neon.tech) to create a free PostgreSQL database.

    Create a `.env` file in the `backend` directory and add the following environment variable:

    ```
    DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
    ```

    Replace the connection string with your actual Neon database connection string from the Neon dashboard.

3.  **Run database migrations:**

    ```bash
    alembic upgrade head
    ```

4.  **Run the application:**

    ```bash
    uvicorn backend.src.main:app --reload
    ```

    The application will be available at `http://localhost:8000`.

## Deployment

To deploy the backend, you can use a platform like Heroku, Vercel, or AWS.

### Heroku

1.  **Create a Heroku app:**

    ```bash
    heroku create
    ```

2.  **Set the `DATABASE_URL` environment variable:**

    ```bash
    heroku config:set DATABASE_URL=postgresql://user:password@host:port/database
    ```

3.  **Push the code to Heroku:**

    ```bash
    git push heroku main
    ```

### Vercel

1.  **Create a Vercel project:**

    Create a new project on Vercel and connect it to your Git repository.

2.  **Set the `DATABASE_URL` environment variable:**

    In the Vercel project settings, add the `DATABASE_URL` environment variable.

3.  **Deploy the application:**

    Vercel will automatically deploy the application when you push changes to your Git repository.
