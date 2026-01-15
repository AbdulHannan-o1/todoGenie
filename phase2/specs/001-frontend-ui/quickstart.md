# Quickstart: Frontend UI/UX

This guide provides instructions to set up and run the `001-frontend-ui` feature locally.

## Prerequisites

*   Node.js (LTS version recommended)
*   npm or Yarn
*   Access to the backend API (running locally or deployed)

## Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd phase2/frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    # or
    yarn install
    ```

3.  **Configure Environment Variables**:
    Create a `.env.local` file in the `phase2/frontend` directory based on `.env.example`.
    Example `.env.local`:
    ```
    NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000/api
    ```
    *Ensure `NEXT_PUBLIC_BACKEND_API_URL` points to your running backend API.*

## Running the Application

1.  **Start the development server**:
    ```bash
    npm run dev
    # or
    yarn dev
    ```

2.  **Access the application**:
    Open your browser and navigate to `http://localhost:3000` (or the port indicated in your terminal).

## Building for Production

1.  **Build the application**:
    ```bash
    npm run build
    # or
    yarn build
    ```

2.  **Start the production server**:
    ```bash
    npm start
    # or
    yarn start
    ```
    The application will be available at `http://localhost:3000`.
