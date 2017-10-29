import {Grid, Row} from 'react-bootstrap';
import React, {Component} from 'react';
import MakeBarChart from './MakeBarChart';

class Dashboard extends Component {
  render() {
    return (
      <Row>
        <MakeBarChart task_name="make_model_count_top20"/>
        <MakeBarChart task_name="make_model_price_top20"/>
        <MakeBarChart task_name="make_year_count"/>
      </Row>
    );
  }
}

export default Dashboard;
