
import React from 'react';

function App() {
  return (
    <iframe
      src={process.env.PUBLIC_URL + '/home.html'}
      title="Anew Home"
      style={{ width: '100vw', height: '100vh', border: 'none' }}
    />
  );

}

export default App;
