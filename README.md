# WearCast 🌤️

**AI-Powered Weather & Clothing Assistant**

WearCast is an intelligent chat application that combines weather data, AI-powered recommendations, and user personalization to help you make informed decisions about what to wear based on current weather conditions.

## 🚀 Pivotal Capabilities

### 🌦️ **Weather Integration**
- Real-time weather data from OpenWeatherMap API
- Location-based weather information using IP geolocation
- Detailed weather metrics including temperature, wind speed, and conditions
- Turkish language support for weather descriptions

### 👕 **AI-Powered Clothing Recommendations**
- Intelligent clothing suggestions based on weather conditions
- Personalized recommendations considering user preferences
- Context-aware outfit planning for different activities
- Seasonal and weather-appropriate clothing guidance

### 💬 **Advanced Chat Interface**
- Real-time AI conversations powered by Google Gemini
- Markdown support with syntax highlighting for code blocks
- Conversation history management with persistent storage
- Typing indicators and real-time message updates
- Dark/Light theme toggle for enhanced user experience

### 👤 **User Management & Personalization**
- Secure user authentication and registration
- Comprehensive user profiles with personal details
- Age calculation and validation
- Gender and location-based customization
- Profile management with edit capabilities

### 🔐 **Security & Data Management**
- JWT-based authentication system
- Secure password validation with strength requirements
- Supabase integration for reliable data storage
- CORS configuration for secure cross-origin requests
- Account management with email and password updates

### 📱 **Modern UI/UX**
- Responsive design that works on desktop and mobile
- Intuitive sidebar navigation for conversation management
- Real-time notifications and toast messages
- Auto-resizing text input for better user experience
- Loading states and error handling

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WearCast
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   Create a `.env` file in the `backend` directory with the following variables:
   ```env
   OPENWEATHER_API_KEY=your_openweather_api_key
   GEMINI_API_KEY=your_gemini_api_key
   IP_API_KEY=your_ipgeolocation_api_key
   SUPABASE_URL=your_supabase_url
   SUPABASE_API_KEY=your_supabase_api_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   SUPABASE_JWT_SECRET=your_supabase_jwt_secret
   ```

5. **Run the backend server**
   ```bash
   python app.py
   ```
   The backend will start on `http://127.0.0.1:5000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Configure backend URL**
   Open `script.js` and update the `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'http://127.0.0.1:5000'; // Change to your backend URL
   ```

3. **Serve the frontend**
   You can use any static file server. For development:
   ```bash
   # Using Python (if you have Python installed)
   python -m http.server 5500
   
   # Using Live Server extension in VS Code
   # Right-click on index.html and select "Open with Live Server"
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:5500`

## 🔑 API Keys Setup

### Required API Keys

1. **OpenWeatherMap API Key**
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your API key from the dashboard
   - Add to `.env` as `OPENWEATHER_API_KEY`

2. **Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add to `.env` as `GEMINI_API_KEY`

3. **IP Geolocation API Key**
   - Sign up at [IPGeolocation.io](https://ipgeolocation.io/)
   - Get your API key from the dashboard
   - Add to `.env` as `IP_API_KEY`

4. **Supabase Configuration**
   - Create a project at [Supabase](https://supabase.com/)
   - Get your project URL and API keys from Settings > API
   - Add to `.env`:
     - `SUPABASE_URL`
     - `SUPABASE_API_KEY`
     - `SUPABASE_SERVICE_ROLE_KEY`
     - `SUPABASE_JWT_SECRET`

## 📁 Project Structure

```
WearCast/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   └── src/
│       ├── core/
│       │   ├── engine.py      # AI engine configuration
│       │   └── prompts.py     # AI prompts and templates
│       ├── routes/
│       │   ├── auth.py        # Authentication endpoints
│       │   └── chat.py        # Chat and conversation endpoints
│       ├── schemas.py         # Data validation schemas
│       └── utils/
│           ├── auth.py        # Authentication utilities
│           ├── functions.py   # Weather and utility functions
│           └── ip.py          # IP geolocation utilities
├── frontend/
│   ├── index.html            # Main HTML file
│   ├── script.js             # Main JavaScript application
│   ├── styles.css            # Application styles
│   └── markdown-test.html    # Markdown testing page
└── README.md                 # This file
```

## 🚀 Features

### For Users
- **Smart Weather Integration**: Get real-time weather data for your location
- **AI Clothing Recommendations**: Receive personalized outfit suggestions
- **Conversation History**: Save and manage your chat conversations
- **User Profiles**: Customize your experience with personal details
- **Responsive Design**: Use on any device with a modern interface

### For Developers
- **RESTful API**: Clean, documented API endpoints
- **Modular Architecture**: Well-organized code structure
- **Error Handling**: Comprehensive error management
- **Security**: JWT authentication and input validation
- **Extensible**: Easy to add new features and integrations

## 🔧 Configuration Notes

### Backend Configuration
- The backend runs on port 5000 by default
- CORS is configured for local development
- Debug mode is enabled for development

### Frontend Configuration
- **Important**: Update the `API_BASE_URL` in `script.js` to match your backend URL
- The frontend expects the backend to be running on the configured URL
- All API calls are made relative to the base URL

### Environment Variables
Make sure all required environment variables are set in your `.env` file:
- `OPENWEATHER_API_KEY`: For weather data
- `GEMINI_API_KEY`: For AI chat functionality
- `IP_API_KEY`: For location detection
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_API_KEY`: Your Supabase API key
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key
- `SUPABASE_JWT_SECRET`: Your Supabase JWT secret

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check if all environment variables are set
   - Ensure Python dependencies are installed
   - Verify port 5000 is not in use

2. **Frontend can't connect to backend**
   - Verify the `API_BASE_URL` in `script.js` is correct
   - Ensure the backend is running
   - Check browser console for CORS errors

3. **API calls failing**
   - Verify all API keys are valid and active
   - Check the backend logs for detailed error messages
   - Ensure your Supabase database is properly configured

4. **Weather data not loading**
   - Verify your OpenWeatherMap API key is valid
   - Check if the IP geolocation service is working
   - Ensure your location is supported by the weather service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🙏 Acknowledgments

- OpenWeatherMap for weather data
- Google Gemini for AI capabilities
- IPGeolocation.io for location services
- Supabase for backend services
- Font Awesome for icons
- Marked.js for markdown parsing
- Prism.js for syntax highlighting

---

**WearCast** - Making weather-based clothing decisions easier with AI! 🌤️👕
