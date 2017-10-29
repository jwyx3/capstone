import React, { Component } from 'react'
import PropTypes from 'prop-types'
import VegaLite from 'react-vega-lite';


export default class MakeBChart extends Component {
  render() {
    const { d3 } = this.props;
    return (
      <VegaLite spec={d3.spec} data={d3.data} renderer="svg"/>
    )
  }
}

MakeBChart.propTypes = {
  d3: PropTypes.object.isRequired
}
