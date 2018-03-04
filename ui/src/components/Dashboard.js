import React from 'react';
import NetWorth from './home/NetWorth';
import TopCurrencies from './home/TopCurrencies';
import StockHistory from './StockHistory';

const Dashboard = () => (
  <div className="container">
    <div className="row">
      <NetWorth />
      <TopCurrencies />
    </div>
    <div className="row">
      <StockHistory />
    </div>
  </div>
);

export default Dashboard;
