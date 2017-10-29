import React, { Component } from 'react'
import { Grid, Tab, Tabs, Row } from 'react-bootstrap';
import { Provider } from 'react-redux'
import configureStore from '../configureStore'
import Dashboard from './Dashboard'

const store = configureStore()

export default class Root extends Component {
  render() {
    return (
      <Provider store={store}>
          <Tabs defaultActiveKey={1}>
            <Grid>
              <Tab eventKey={1} title="Dashboard"><Dashboard/></Tab>
            </Grid>
          </Tabs>
      </Provider>
    )
  }
}
