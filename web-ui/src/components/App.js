import React from 'react';
import { Link } from 'react-router';

const App = ({ children }) => (
  <div>
    <header>
      <h1>White wave</h1>
      <Link to="/events">events</Link>
    </header>
    <section>
      {children || 'Welcome to React Starterify'}
    </section>
  </div>
);

App.propTypes = { children: React.PropTypes.object };

export default App;
