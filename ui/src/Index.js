import React from 'react';
import { render } from 'react-dom';
import { Router, Route, hashHistory } from 'react-router';
import App from './components/App';
import Events from './components/Events';
import Predictions from './components/Predictions';

window.React = React;

render(
  (<Router history={hashHistory}>
    <Route path="/" component={App}>
      <Route path="/events" component={Events} />
      <Route path="/predictions" component={Predictions} />
    </Route>
  </Router>), document.getElementById('content')
);
