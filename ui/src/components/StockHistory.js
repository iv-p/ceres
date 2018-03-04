import React from 'react';
import axios from 'axios';

class StockHistory extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      stocks: []
    };

    axios.get('http://localhost:1337/stocks/history')
      .then(res => {
        const stocks = res.data;
        stocks.map((stock) => {
          stock.diff = stock.sell ? stock.quantity * (stock.sell.price - stock.buy.price) : null;
          stock.status = 'text-warning';
          if (stock.diff) {
            stock.status = stock.diff > 0 ? 'text-success' : 'text-danger';
          }
          return stock;
        });
        stocks.sort((a, b) => (a.timestamp > b.timestamp ? 1 : 0));
        this.setState({ stocks });
      });
  }

  render() {
    let stocksList = this.state.stocks.map((stock) =>
      <tr className={stock.status}>
        <td>{(new Date(stock.buy.timestamp * 1000)).toUTCString()}</td>
        <td>{stock.symbol}</td>
        <td>{stock.quantity.toFixed(6)}</td>
        <td>{stock.buy.price.toFixed(6)}</td>
        <td>{(stock.buy.price * stock.quantity).toFixed(6)}</td>
        <td>{stock.sell ? (stock.sell.price * stock.quantity).toFixed(6) : ''}</td>
        <td>{stock.sell ? (stock.sell.price).toFixed(6) : ''}</td>
        <td>{stock.sell ? (stock.quantity * (stock.sell.price - stock.buy.price)).toFixed(6) : ''}</td>
      </tr>
    );

    return (
      <table className="table">
        <thead>
          <tr>
            <th>timestamp</th>
            <th>currency</th>
            <th>quantity</th>
            <th>buy price</th>
            <th>total buy</th>
            <th>sell price</th>
            <th>total sell</th>
            <th>profit</th>
          </tr>
        </thead>
        <tbody>
          {stocksList}
        </tbody>
      </table>
    );
  }
}

export default StockHistory;
