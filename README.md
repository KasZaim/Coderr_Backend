 Coderr backend

The Coderr Backend is the server-side component of the Coderr platform, a Fiverr clone built with Django and Django Rest Framework (DRF). It provides robust APIs for managing users, profiles, offers, orders, reviews, and other functionalities required for a freelance marketplace.

## Features

- User Profiles: Manage customer and business user profiles.

- Offers: Create, update, and list service offers with detailed options (e.g., Basic, Standard, Premium).

- Orders: Handle orders between customers and business users with statuses like in_progress, completed, and cancelled.

- Reviews: Enable customers to review business users with ratings and comments.

- Filter and Search: Advanced filtering and search for offers and reviews.

- Statistics: Provide metrics such as total orders, completed orders, and average ratings.

## Installation

### Prerequisites

- Python 3.x
- Django 3.x or 4.x
- Node.js (optional if you want to use additional frontend tools)

### Setup Instructions

1. **Clone this repository (Backend) :**
   ```bash
   git clone https://github.com/KasZaim/Coderr_Backend.git
   cd Coderr_Backend
  
**2.Create and activate a virtual environment:**  
  
  `python -m venv venv`
  
  `source venv/bin/activate`  # For Linux/Mac
  
  `venv\Scripts\activate`     # For Windows
  
**3.Install dependencies:**

  `pip install -r requirements.txt`

**4.Run migrations and create a Superuser:**
 
 `python manage.py migrate`
 
 `python manage.py createsuperuser`  # Optional: create a superuser for the admin panel
 
 `python manage.py runserver`

**5.Set up the frontend:**

- Clone the Frontend from the Repository  `https://github.com/KasZaim/Coderr_frontend.git`

- Navigate to the frontend project and start the live server:

- Start the live server (e.g., using a local development environment like VS Code)

### Usage

Admin Panel: Access at http://127.0.0.1:8000/admin/ with your superuser account.

# API Endpoints:

### **Authentication**
- `/api/auth/register/`  
  Register new users.
  
- `/api/auth/login/`  
  Log in existing users.

---

### **User Profiles**
- `/api/profiles/`  
  Manage user profiles (create, retrieve, update, delete).

---

### **Offers**
- `/api/offers/`  
  Manage service offers and their details.

---

### **Orders**
- `/api/orders/`  
  Handle orders between customers and business users.

---

### **Reviews**
- `/api/reviews/`  
  Create and manage reviews for business users.

---

### **Statistics**
- `/api/orders/<business_user_id>/count/`  
  Get the count of in-progress orders for a business user.

- `/api/orders/<business_user_id>/completed/`  
  Get the count of completed orders for a business user.

Technologies

Django and Django REST Framework
JavaScript (frontend)
SQLite or PostgreSQL for the database
