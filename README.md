8bcc5d2c-c67e-4025-b5d4-d0d594a69a58:46d34c28967254bd1bcecf17aa6a0fd9
# Velgo Agrisolutions - Agricultural Consultancy Platform

A modern, full-stack agricultural consultancy platform connecting farmers with expert services through an intuitive web interface.

---

## 📋 About The Project

Velgo Agrisolutions is a comprehensive solution for agricultural consultancy services. Farmers can browse services, book consultations, and track their requests through an easy-to-use dashboard.

**Tech Stack:** MongoDB + JWT Authentication + Flask + HTML/CSS/JavaScript  
**Features:** Service booking, consultation scheduling, admin panel, bilingual support (English/Tamil)

## ✨ Key Features

* **Secure Authentication:** JWT-based user authentication with bcrypt password hashing
* **MongoDB Backend:** Scalable database with PyMongo integration
* **Service Booking:** Book agricultural services like Soil Testing, Crop Planning, AI & IoT Farming
* **Consultation Requests:** Schedule on-site or office consultations
* **User Dashboard:** Track booking status (Pending, Accepted, Completed, Rejected)
* **Admin Panel:** Manage bookings and update request statuses
* **Bilingual Support:** Toggle between English and Tamil
* **Modern UI/UX:** Responsive design with AOS animations

## 💻 Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6)
* **Backend:** Flask (Python)
* **Database:** MongoDB Atlas / Local MongoDB
* **Authentication:** JWT (JSON Web Tokens)
* **Security:** bcrypt password hashing
* **Libraries:** AOS (Animate on Scroll), Font Awesome

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* MongoDB (local or Atlas account)
* Git

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sarjanthecoder/AGRI-SOLUTIONS.git
   cd AGRI-SOLUTIONS
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Create .env file (use .env.example as template)
   cp .env.example .env
   
   # Edit .env and add your MongoDB connection string
   # MONGODB_URI=mongodb://localhost:27017/velgo_agri
   # Or for MongoDB Atlas:
   # MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/velgo_agri
   ```

4. **Initialize database:**
   ```bash
   python init_db.py
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open in browser:**
   ```
   http://localhost:5000
   ```

### Default Admin Login

* Email: `admin@velgo.com`
* Password: `admin123`

**⚠️ Change admin password in production!**

## 📂 Project Structure

```
velgo-agri-solution/
├── static/              # Static files (CSS, JS, images)
│   ├── auth.js         # JWT authentication module
│   └── app.js          # Main application logic
├── templates/           # HTML templates
│   ├── index.html      # Homepage
│   └── admin.html      # Admin dashboard
├── app.py              # Flask application
├── models.py           # MongoDB models
├── auth.py             # JWT authentication
├── config.py           # Configuration management
├── init_db.py          # Database initialization
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variables template
```

## 🔒 Security Features

* JWT token-based authentication
* Bcrypt password hashing
* Session management
* Input validation
* MongoDB connection security
* Environment variable configuration

## 🌐 Deployment

### MongoDB Atlas Setup

1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Add database user with read/write permissions
4. Whitelist your IP address (or 0.0.0.0/0 for all)
5. Get connection string and add to `.env`

### Production Deployment

* Use `gunicorn` for production WSGI server
* Enable HTTPS
* Change all default passwords
* Update `SECRET_KEY` and `JWT_SECRET` in `.env`
* Set up MongoDB backups

## 📜 License

Distributed under the MIT License.

## 👤 Contact

Sarjan - [@sarjanthecoder](https://github.com/sarjanthecoder)

Project Link: [https://github.com/sarjanthecoder/AGRI-SOLUTIONS](https://github.com/sarjanthecoder/AGRI-SOLUTIONS)

---

**Made with ❤️ for farmers**
