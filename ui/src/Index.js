import React from 'react';
import { render } from 'react-dom';
import { Router, Route, hashHistory, IndexRoute } from 'react-router';
import App from './components/App';
import Events from './components/Events';
import Predictions from './components/Predictions';
import Dashboard from './components/Dashboard';
import StockHistory from './components/StockHistory';

window.React = React;

render(
  (<Router history={hashHistory}>
    <Route path="/" component={App}>
      <IndexRoute component={Dashboard} />
      <Route path="/dashboard" component={Dashboard} />
      <Route path="/events" component={Events} />
      <Route path="/predictions" component={Predictions} />
      <Route path="/stock-history" component={StockHistory} />
    </Route>
  </Router>), document.getElementById('content')
);
