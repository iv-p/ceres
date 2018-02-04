import React from 'react';
import { Table } from 'react-bootstrap';
import axios from 'axios';

class Events extends React.Component {
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
    let eventList = this.state.events.map((event) =>
      <tr>
        <td>{event.timestamp}</td>
        <td>{event.currency}</td>
        <td>{event.event}</td>
        <td>{event.status}</td>
      </tr>
    );

    return (
      <Table striped bordered condensed hover>
        <thead>
          <tr>
            <th>timestamp</th>
            <th>currency</th>
            <th>event</th>
            <th>status</th>
          </tr>
        </thead>
        <tbody>
          {eventList}
        </tbody>
      </Table>
    );
  }
}

export default Events;
