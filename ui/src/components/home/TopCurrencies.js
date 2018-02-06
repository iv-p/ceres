import React from 'react';
import axios from 'axios';

class TopCurrencies extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      events: []
    };

    axios.get('http://localhost:1337/events')
      .then(res => {
        const events = res.data;
        this.setState({ events });
      });
  }

  render() {
    const tableStyle = {
      marginBottom: '0px'
    };

    return (
      <div className="card col">
        <div className="card-block">
          <h4 className="card-title">
            top 5 currencies
          </h4>
          <table className="table table-sm table-hover" style={tableStyle}>
            <tbody>
              <tr>
                <th scope="row">XLM</th>
                <td>$123.42</td>
                <td className="text-danger">-13.23%</td>
              </tr>
              <tr>
                <th scope="row">XRP</th>
                <td>$1223.42</td>
                <td className="text-success">262.23%</td>
              </tr>
              <tr>
                <th scope="row">XLM</th>
                <td>$123.42</td>
                <td className="text-danger">-13.23%</td>
              </tr>
              <tr>
                <th scope="row">XLM</th>
                <td>$123.42</td>
                <td className="text-danger">-13.23%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

export default TopCurrencies;
