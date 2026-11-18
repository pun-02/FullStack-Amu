# CyberShield – Vulnerability Management System

CyberShield is a full-stack vulnerability management system designed to manage, store, and view security vulnerabilities.

## Project Overview

The backend is developed using Python Flask and MongoDB. It provides authentication and vulnerability management functionality.

## Technologies Used

- Python
- Flask
- MongoDB
- PyMongo
- JWT Authentication
- JSON (NVD Vulnerability Dataset)

## Backend Installation

### 1. Clone the repository

```bash
git clone https://github.com/pun-02/FullStack-Amu.git
cd FullStack-Amu
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root and add:

```env
JWT_SECRET_KEY=your_secret_key_here
```

Replace the example with your own secret key. Do not upload your `.env` file to GitHub.

## MongoDB Setup

CyberShield uses MongoDB to store user and vulnerability data.

1. Install MongoDB Community Server on your computer.
2. Make sure the MongoDB service is running.
3. The backend connects to MongoDB using:

```text
mongodb://127.0.0.1:27017/
```

The application uses a database named `cybershield`.


## NVD Vulnerability Dataset Setup

The NVD 2025 JSON dataset is provided separately as a GitHub Release asset because of its large file size.

**Download the dataset:**

[CyberShield NVD Dataset 2025 – Download](https://github.com/pun-02/FullStack-Amu/releases/tag/v1.0.0)

After downloading:

1. Open the CyberShield project folder.
2. Open the `data` folder.
3. Place the downloaded JSON file inside it.
4. Make sure its filename is exactly:

```text
nvdcve-2.0-2025.json
```

## Running the Backend

From the project root directory, run:

```bash
python app.py
```

The Flask backend starts on:

```text
http://127.0.0.1:5001
```

You can check whether the backend is running by opening:

```text
http://127.0.0.1:5001/health
```

## Project Status

- Backend: Developed using Flask and MongoDB.
- Frontend: To be developed.



