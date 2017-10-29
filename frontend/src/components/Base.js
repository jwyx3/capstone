import React, {Component} from 'react';
import { Grid, Tab, Tabs, Row } from 'react-bootstrap';
import Home from './Home';
import Dashboard from './Dashboard';

class Base extends Component {
  render() {
    return (
      <Grid>
        <Row>
          <Tabs defaultActiveKey={1}>
            <Tab eventKey={1} title="Home"><Home/></Tab>
            <Tab eventKey={2} title="Dashboard"><Dashboard/></Tab>
          </Tabs>
        </Row>
      </Grid>
    );
  }
}

export default Base;
