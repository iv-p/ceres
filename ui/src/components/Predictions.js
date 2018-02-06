import React from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import NetWorth from './home/NetWorth';
import TopCurrencies from './home/TopCurrencies';

class Predictions extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      prices: [],
      value: ''
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  getPredictions(currency) {
    // axios.get(`http://localhost:1337/predictions/currency/${currency}`)
    //   .then(res => {
    //     const predictions = res.data.map(prediction => {
    //       const pred = prediction;
    //       pred.minute = prediction.price_predictions[0];
    //       pred.hour = prediction.price_predictions[1];
    //       pred.timestamp = new Date(prediction.timestamp * 1000);
    //       return pred;
    //     });
    //     this.setState({ predictions });
    //   });
    axios.get(`http://localhost:1337/price/currency/${currency}`)
      .then(res => {
        const prices = res.data;
        console.log(prices);
        this.setState({ prices });
      });
  }

  handleChange(event) {
    this.setState({ value: event.target.value });
  }

  handleSubmit(event) {
    event.preventDefault();
    if (this.state.value !== '') {
      this.getPredictions(this.state.value);
    }
  }

  render() {
    return (
      <div className="container">
        <div className="row">
          <NetWorth />
          <TopCurrencies />
        </div>
        <form onSubmit={this.handleSubmit}>
          <label>
            Name:
            <input type="text" value={this.state.value} onChange={this.handleChange} />
          </label>
          <input type="submit" value="Submit" />
        </form>
        <LineChart
          width={1280}
          height={500}
          data={this.state.prices}
          margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
        >
          <XAxis dataKey="timestamp" />
          <YAxis domain={['auto', 'auto']} />
          <Legend />
          <Tooltip />
          <Line type="monotone" dot={false} dataKey="price" stroke="#8884d8" />
          {/* <Line type="monotone" dot={false} dataKey="hour" stroke="#0084d8" /> */}
        </LineChart>
      </div>
    );
  }
}

export default Predictions;
