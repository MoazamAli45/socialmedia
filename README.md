# Social Media App Frontend

A modern social media application built with Vue.js 3, Tailwind CSS, and integrated with Django REST API.

## Features

- **User Authentication**: Login, signup, and logout
- **Profile Management**: Edit profile, upload profile pictures
- **Post Creation**: Create posts with text and images
- **Social Interactions**: Like posts, follow/unfollow users
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Vue.js 3**: Composition API, reactive state management
- **Pinia**: State management
- **Vue Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **Headless UI**: Unstyled, accessible UI components
- **Axios**: HTTP client for API calls
- **Vite**: Build tool and development server

## Project Structure

```
src/
├── components/          # Reusable Vue components
├── views/              # Page components
├── stores/             # Pinia stores
├── services/           # API services
├── router/             # Vue Router configuration            
└── main.js            # Application entry point
```

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

## API Integration

The frontend is configured to work with your Django REST API:

- **Base URL**: `http://localhost:8000/api` (Django API Locally running)
- **Authentication**: JWT tokens stored in localStorage
- **File Uploads**: Cloudinary integration for images

## Key Components

### Authentication
- Login/Signup forms with validation
- JWT token management
- Protected routes

### Posts
- Create posts with text and images
- Like/unlike functionality
- Infinite scroll loading

### Profile
- View user profiles
- Edit profile information
- Upload profile pictures
- Follow/unfollow users

### Navigation
- Responsive navbar
- User menu with dropdown

## Customization

### Styling
- Component-specific styling using Tailwind classes

### API Endpoints
- Update `src/services/api.js` for API configuration
- Modify store actions for different endpoints

## Development Tips

1. **State Management**: Use Pinia stores for global state
2. **Component Composition**: Leverage Vue 3 Composition API
3. **Error Handling**: Implement proper error boundaries
4. **Performance**: Use lazy loading for routes
5. **Accessibility**: Ensure proper ARIA labels and keyboard navigation

## Production Deployment

1. **Build the project**:
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder** to your web server



This frontend provides a complete social media experience that integrates seamlessly with your Django REST API backend.****
