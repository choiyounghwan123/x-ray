# MLOps Pipeline Frontend

A modern React frontend for managing and monitoring MLOps pipelines.

## Features

- **Dashboard**: Overview of your ML models and training jobs
- **Training**: Monitor and manage model training pipelines
- **Models**: Manage trained models and deployments
- **Monitoring**: Real-time monitoring of model performance

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Lucide React** for icons
- **Axios** for API calls

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
  components/     # Reusable UI components
  pages/         # Page components
  utils/         # Utility functions
  types/         # TypeScript type definitions
  App.tsx        # Main app component
  main.tsx       # App entry point
  index.css      # Global styles
```

## Development

The app uses a modern development setup with:
- Hot module replacement for fast development
- TypeScript for type safety
- ESLint for code quality
- Tailwind CSS for rapid styling

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready to be served by any static hosting service. 