# WeatherWise 🌦️

**WeatherWise** is an AI-powered weather application built with **Flutter** and **Django REST Framework**. It combines real-time weather data with machine learning to provide weather forecasts, predictions, alerts, air-quality information, astronomy data, and personalized recommendations.

The application is designed to go beyond simply displaying the current temperature by helping users understand upcoming weather conditions and make better decisions based on them.

---

## ✨ Features

* 🌤️ **Current Weather**

    * Temperature
    * Weather condition
    * Humidity
    * Wind speed
    * Location information

* 📅 **7-Day Weather Forecast**

    * Daily weather predictions
    * Temperature trends
    * Weather conditions

* 🤖 **AI Weather Prediction**

    * Machine-learning-based temperature prediction
    * Rain prediction
    * Historical weather data used for model training

* 🌫️ **Air Quality**

    * Air-quality information
    * Air-quality category and status

* ⚠️ **Weather Alerts**

    * Weather-related warnings and alerts

* 🌅 **Astronomy Information**

    * Sunrise
    * Sunset
    * Moonrise
    * Moonset
    * Moon phase

* 💡 **Personalized Weather Advice**

    * Recommendations based on weather conditions
    * Practical advice for different user activities

* 📍 **Location Search**

    * Search for different cities
    * Location-based weather information

* 🎨 **Theme Support**

    * Light mode
    * Dark mode
    * System theme

---

## 🏗️ Architecture

WeatherWise follows a **Flutter + Django REST API** architecture.

```text
                    ┌─────────────────────┐
                    │      Flutter App    │
                    │                     │
                    │  UI / Screens       │
                    │  Widgets            │
                    │  Models             │
                    │  Services            │
                    └──────────┬──────────┘
                               │
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │   Django Backend    │
                    │                     │
                    │ Django REST API     │
                    │ Weather Services    │
                    │ Weather Models      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
             Weather Data            ML Models
                                   
                              ┌───────────────┐
                              │ Temperature   │
                              │ Prediction    │
                              │               │
                              │ Rain          │
                              │ Prediction    │
                              └───────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* **Flutter**
* **Dart**
* **Riverpod**
* Material Design

### Backend

* **Python**
* **Django**
* **Django REST Framework**

### Machine Learning

* **NumPy**
* **Pandas**
* **Scikit-learn**
* Joblib

### Data & APIs

* Weather API
* Historical weather data
* RESTful communication between Flutter and Django

---

## 🧠 Machine Learning

WeatherWise includes machine-learning functionality for weather prediction.

The backend contains trained models for:

```text
Temperature Prediction
        +
Rain Prediction
```

The models are stored in:

```text
backend/weather/ml_models/
├── temperature_model.joblib
└── rain_model.joblib
```

Historical weather data is processed and used to train the prediction models.

The Django backend exposes the prediction functionality through the application's API, while the Flutter frontend presents the predictions to the user.

---

## 📂 Project Structure

```text
WeatherWise/
│
├── android/
├── ios/
├── linux/
├── macos/
├── web/
├── windows/
│
├── assets/
│   └── icon/
│
├── lib/
│   ├── core/
│   │   ├── theme/
│   │   └── utils/
│   │
│   ├── models/
│   │
│   ├── screens/
│   │   ├── home/
│   │   ├── location/
│   │   ├── profile/
│   │   ├── search/
│   │   └── settings/
│   │
│   ├── services/
│   │
│   ├── widgets/
│   │   └── home/
│   │
│   └── main.dart
│
├── backend/
│   ├── weather/
│   │   ├── management/
│   │   ├── migrations/
│   │   ├── ml_models/
│   │   ├── advice_service.py
│   │   ├── ml_service.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── weatherwise_backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
│
├── assets/
├── pubspec.yaml
├── analysis_options.yaml
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

* Flutter SDK
* Dart SDK
* Python 3.x
* Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/WeatherWise.git
cd WeatherWise
```

---

## 2. Flutter Setup

Install Flutter dependencies:

```bash
flutter pub get
```

Run the Flutter application:

```bash
flutter run
```

---

## 3. Django Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## 4. Environment Variables

Create a `.env` file inside the `backend` directory.

Use `.env.example` as a reference:

```env
SECRET_KEY=your-secret-key
```

Do not commit the `.env` file to GitHub.

---

## 5. Run Django

From the `backend` directory:

```bash
python manage.py migrate
```

Then start the Django development server:

```bash
python manage.py runserver
```

The backend will be available at:

```text
http://127.0.0.1:8000/
```

---

## 🔄 Running the Complete Application

Run the Django backend first:

```bash
cd backend
venv\Scripts\activate
python manage.py runserver
```

Then open another terminal in the project root and run:

```bash
flutter run
```

The Flutter application communicates with the Django REST API to retrieve weather information and prediction results.

---

## 🔐 Security

Sensitive configuration is stored using environment variables.

The following files are intentionally excluded from version control:

```text
.env
venv/
db.sqlite3
.dart_tool/
build/
```

A `.env.example` file is included to show the required environment variables without exposing private credentials.

---

## 📌 Future Improvements

Potential improvements for future versions include:

* User authentication and profiles
* Push notifications for severe weather alerts
* More advanced weather prediction models
* Improved ML model accuracy with larger datasets
* Weather visualization and graphs
* Historical weather charts
* Cloud deployment
* Automated model retraining
* Production database integration

---

## 👨‍💻 Author

**Anshul Arohi**

WeatherWise — AI-powered weather application built using Flutter, Django REST Framework, and Machine Learning.

---

## ⭐ Project

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.
