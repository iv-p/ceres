import React from 'react';
import axios from 'axios';
import { Eth } from 'react-cryptocoins';

class NetWorth extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      worth: 0
    };

    axios.get('http://localhost:1337/worth')
      .then(res => {
        this.setState({ worth: Math.floor(res.data * 1000) / 1000 });
      });
  }

  render() {
    return (
      <div className="card col">
        <div className="card-block">
          <h4 className="card-title">net worth</h4>
          <h1 className="display-1"><Eth size={64} /> {this.state.worth}</h1>
        </div>
      </div>
    );
  }
}

export default NetWorth;
