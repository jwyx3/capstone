import { Row, Col } from 'react-bootstrap';
import { Form, FormGroup, FormControl, InputGroup } from 'react-bootstrap';
import React, { Component } from 'react';
import Client, { parseId, apiClient } from '../util/ApiClient';
import VegaLite from 'react-vega-lite';
import _ from 'lodash';


class MakeBarChartControl extends Component {
  constructor(props) {
    super(props);
    this.state = {makes: []};
    this.getInitialMakes();
  }

  getInitialMakes() {
    const self = this;
    Client.usedMakes((error, response) => {
      if (error) {
        console.log(error);
        return;
      }
      self.setState({
        makes: response.data.results
      });
    });
  }

  renderMakeOptions(makes) {
    return makes.map((make, i) => {
      const id = parseId(make.url);
      const name = _.startCase(make.name);
      return (
        <option key={id} value={id}>{name}</option>
      );
    });
  }

  render() {
    return (
      <Form inline>
        <FormGroup controlId="Make">
          <InputGroup bsSize="small">
            <InputGroup.Addon>Make</InputGroup.Addon>
            <FormControl componentClass="select"
              onChange={(event) => this.props.handleChange(event, 'make')}>
              <option key="-1" value="--">--</option>
              {this.renderMakeOptions(this.state.makes)}
            </FormControl>
          </InputGroup>
        </FormGroup>
        {/* <FormGroup controlId="Order">
          <InputGroup bsSize="small">
            <InputGroup.Addon>Order</InputGroup.Addon>
            <FormControl componentClass="select"
              onChange={(event) => this.props.handleChange(event, 'order')}>
              <option value="asc">ASC</option>
              <option value="desc">DESC</option>
            </FormControl>
          </InputGroup>
        </FormGroup>
        <FormGroup controlId="Limit">
          <InputGroup bsSize="small">
            <InputGroup.Addon>Limit</InputGroup.Addon>
            <FormControl componentClass="select"
              onChange={(event) => this.props.handleChange(event, 'limit')}>
              <option value="20">20</option>
              <option value="15">15</option>
              <option value="15">10</option>
            </FormControl>
          </InputGroup>
        </FormGroup> */}
      </Form>
    );
  }
}


class MakeBarChart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      spec: null,
      data: null,
      settings: {
        make: null,
        order: 'desc',
        limit: 20,
      }
    };
  }

  getUrl(make) {
    return `/static/d3/${this.props.task_name}/${_.lowerCase(make)}.json`
  }

  handleChange(event, key) {
    const self = this;

    let settings = {};
    settings[key] = _.lowerCase(event.target.value);
    this.setState(_.defaultsDeep({settings: settings}, this.state));

    if (settings.make) {
      apiClient().get(this.getUrl(settings.make))
      .then(function (response) {
        self.setState({
          spec: response.data,
          data: response.data['data'],
        });
      })
      .catch(function (error) {
        throw error;
      });
    }
  }

  render() {
    let spec = this.state.spec;
    let data = this.state.data;
    if (spec) {
      return (
        <Row>
          <Row><Col><MakeBarChartControl handleChange={this.handleChange.bind(this)}/></Col></Row>
          <Row><Col><VegaLite spec={spec} data={data} renderer="svg"/></Col></Row>
        </Row>
      );
    }
    return (
      <Row>
        <Row><Col><MakeBarChartControl handleChange={this.handleChange.bind(this)} /></Col></Row>
      </Row>
    );
  }
}

export default MakeBarChart;
