import React from 'react';
import axios from 'axios';

class NetWorth extends React.Component {
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
    return (
      <div className="card col">
        <div className="card-block">
          <h4 className="card-title">net worth</h4>
          <h1 className="display-1">$1231.31</h1>
        </div>
      </div>
    );
  }
}

export default NetWorth;
