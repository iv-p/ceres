import React from 'react';
import axios from 'axios';

class TopCurrencies extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      stocks: []
    };

    axios.get('http://localhost:1337/stocks/active')
      .then(res => {
        this.setState({ stocks: res.data.slice(0, 5) });
      });
  }

  render() {
    const tableStyle = {
      marginBottom: '0px'
    };

    let stocksList = this.state.stocks.map((stock) =>
      <tr>
        <td>{stock.symbol}</td>
        <td>{Math.floor(stock.quantity * 100) / 100}</td>
        <td>{Math.floor(stock.buy.price * 10000000) / 10000000}</td>
      </tr>
    );

    return (
      <div className="card col">
        <div className="card-block">
          <h4 className="card-title">
            top 5 currencies
          </h4>
          <table className="table table-sm table-hover" style={tableStyle}>
            <tbody>
              {stocksList}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

export default TopCurrencies;
