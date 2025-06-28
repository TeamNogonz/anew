<<<<<<< HEAD
import { RouterProvider } from 'react-router-dom';
import router from './routes';
import './App.css';

function App() {
  return <RouterProvider router={router} />;
=======
import React from 'react';

function App() {
  return (
    <iframe
      src={process.env.PUBLIC_URL + '/home.html'}
      title="Anew Home"
      style={{ width: '100vw', height: '100vh', border: 'none' }}
    />
  );
>>>>>>> 6833d8a ([Add] home page init)
}

export default App;
