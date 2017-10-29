import {Grid, Row} from 'react-bootstrap';
import React, {Component} from 'react';
import AdSearch from './AdSearch';

class Home extends Component {
  render() {
    return (
      <Row>
        <AdSearch onAdClick={(ad) => { console.log(ad); }}/>
      </Row>
    );
  }
}

export default Home;
