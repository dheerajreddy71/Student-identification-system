# Quick Start Guide - Student Identification System

## ✅ System is Ready!

All components are installed and configured. Follow these steps to start using the system:

## 🔐 Login Credentials

**Default Admin Account:**

- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANT**: Change this password after first login!

## 🚀 Starting the System

### 1. Backend (Already Running)

The backend is running on port 8000. If you need to restart it:

```powershell
.\run_backend.ps1
```

### 2. Frontend

In a **new terminal**:

```powershell
cd frontend
npm run dev
```

### 3. Access the Dashboard

Open your browser and go to:

```
http://localhost:3000
```

You'll see a login page. Enter:

- Username: `admin`
- Password: `admin123`

## 📊 Register Students (Important!)

Before you can identify students, you need to register them from the trainset:

In a **new terminal** (with venv activated):

```powershell
.\venv\Scripts\Activate.ps1
python scripts\register_students.py --data_dir trainset
```

This will:

- Process all student photos from the `trainset` folder
- Extract face embeddings using AI models
- Store in database and FAISS index
- Takes about 5-10 minutes

## 🎯 Using the System

After logging in, you'll see 4 tabs:

### 1. 🔍 Identify Student

- Upload a photo or use webcam
- Click "Identify Student"
- System will match against registered students
- Shows top 3 matches with confidence scores

### 2. ➕ Register Student

- Add new students to the database
- Upload their photo
- Enter their details (name, ID, class, etc.)

### 3. 👥 Student Database

- View all registered students
- Search and filter
- Edit student information

### 4. 📊 Statistics

- View system performance metrics
- Identification logs
- Accuracy statistics

## 🔧 Troubleshooting

### Can't Login?

- Make sure backend is running (check terminal for "Uvicorn running on...")
- Check that you're using: `admin` / `admin123`

### No Students Found?

- Run the registration script first (see step above)
- Check that trainset folder has student photos

### Frontend Not Loading?

- Make sure you ran `npm install` in the frontend folder
- Check that port 3000 is not used by another app

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Project README**: See README.md
- **Detailed Setup**: See SETUP_GUIDE.md

## 🎉 You're All Set!

The system is fully configured and ready to use. Enjoy!
