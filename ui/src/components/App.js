import React from 'react';
import { Link } from 'react-router';

const App = ({ children }) => (
  <div>
    <nav className="navbar navbar-toggleable-md navbar-light bg-faded">
      <button
        className="navbar-toggler navbar-toggler-right"
        type="button"
        data-toggle="collapse"
        data-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>
      <Link to="/" className="navbar-brand">White Wave</Link>

      <div className="collapse navbar-collapse" id="navbarSupportedContent">
        <ul className="navbar-nav mr-auto">
          <li className="nav-item">
            <Link to="/events" className="nav-link">Events</Link>
          </li>
          <li className="nav-item">
            <Link to="/predictions" className="nav-link">Predictions</Link>
          </li>
          <li className="nav-item">
            <Link to="/stock-history" className="nav-link">Stock History</Link>
          </li>
        </ul>
      </div>
    </nav>
    {children || 'Welcome to React Starterify'}
  </div>
);

App.propTypes = { children: React.PropTypes.object };

export default App;
