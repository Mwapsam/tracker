
---

# **Truck Tracking Webapp**

## **Overview**
Truck Tracking Webapp is a full-stack application designed to help truck drivers plan trips efficiently by providing **route instructions**, **Electronic Logging Device (ELD) logs**, and real-time tracking.

## **Built With**
### **Frontend**
- TypeScript
- Next.js
- Radix-UI

### **Backend**
- Python
- Django (Django REST Framework)
- PostgreSQL
- Docker

## **Features**
- 🚛 **Trip Planning**: Users enter trip details (pickup & drop-off locations).
- 🗺 **Route Display**: The app displays an interactive map with planned routes.
- ⛽ **Fuel Stops**: Automatic fueling stops every 1,000 miles.
- 🕒 **ELD Log Generation**: Generates **daily log sheets** based on U.S. driving regulations (70 hrs/8 days).

---

## **Getting Started**

### **Setup**
To get a local copy up and running, follow these steps:

#### **Clone the Repository**
```sh
git clone git@github.com:Mwapsam/tracker.git
cd tracker
```

### **Frontend**
1. Navigate to the frontend folder:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the development server:
   ```sh
   npm start
   ```

### **Backend**
1. Activate virtual environment:
   ```sh
   poetry shell
   ```
2. Install dependencies:
   ```sh
   poetry install
   ```
3. Apply migrations:
   ```sh
   poetry run python manage.py migrate
   ```
4. Start the Django server:
   ```sh
   poetry run python manage.py runserver
   ```

---

## **Environment Variables**
Create a `.env` file in the backend and frontend directories and add the following:

### **Backend (.env)**
```env
DJANGO_SECRET_KEY=your_secret_key
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DJANGO_SETTINGS_MODULE=spotter.settings.development
```

### **Frontend (.env.local)**
```env
MAPS_API_KEY=your_map_api_key
```

---

## **Deployment**

### **Deploy Frontend (Vercel)**
```sh
vercel login
vercel init
vercel --prod
```

### **Deploy Backend (Docker)**
```sh
docker-compose build
docker-compose up -d
```

---

## **API Endpoints**
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/api/trip/` | Create a new trip |
| `GET` | `/api/trip/:id/` | Get trip details |
---

## **Author**
👤 **Samuel Chimfwembe**  
- GitHub: [@mwapsam](https://github.com/Mwapsam)  
- Twitter: [@mwapesamuel4](https://twitter.com/mwapesamuel4)  
- LinkedIn: [mwapsam](https://www.linkedin.com/in/mwapsam/)

---

