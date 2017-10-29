import React, { Component } from 'react'
import { Row, Col } from 'react-bootstrap';
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import {
  selectMake,
  fetchD3IfNeeded,
  invalidateMake
} from '../actions'
import MakeBChart from '../components/MakeBChart';
import Picker from '../components/Picker'


class Dashboard extends Component {
  constructor(props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
    this.handleRefreshClick = this.handleRefreshClick.bind(this)
  }

  componentDidMount() {
    const { dispatch, selectedMake } = this.props
    dispatch(fetchD3IfNeeded(selectedMake))
  }

  componentDidUpdate(prevProps) {
    if (this.props.selectedMake !== prevProps.selectedMake) {
      const { dispatch, selectedMake } = this.props
      dispatch(fetchD3IfNeeded(selectedMake))
    }
  }

  handleChange(nextMake) {
    this.props.dispatch(selectMake(nextMake))
    this.props.dispatch(fetchD3IfNeeded(nextMake))
  }

  handleRefreshClick(e) {
    e.preventDefault()

    const { dispatch, selectedMake } = this.props
    dispatch(invalidateMake(selectedMake))
    dispatch(fetchD3IfNeeded(selectedMake))
  }

  render() {
    const { selectedMake, d3, isFetching, lastUpdated } = this.props
    return (
      <Row>
        <Row>
          <Col>
            <Picker value={selectedMake}
              onChange={this.handleChange}
              options={['reactjs', 'frontend']}
            />
          </Col>
        </Row>
        <Row>
          <Col>
            <p>
              {lastUpdated &&
                <span>
                  Last updated at {new Date(lastUpdated).toLocaleTimeString()}.
                  {' '}
                </span>}
              {!isFetching &&
                <a href="#" onClick={this.handleRefreshClick}>
                  Refresh
                </a>}
            </p>
            {isFetching && d3.length === 0 && <h2>Loading...</h2>}
            {!isFetching && d3.length === 0 && <h2>Empty.</h2>}
          </Col>
        </Row>
        {d3.length > 0 &&
          <div style={{ opacity: isFetching ? 0.5 : 1 }}>
            <Row><Col><MakeBChart name="make_model_count_top20"/></Col></Row>
            <Row><Col><MakeBChart name="make_model_price_top20"/></Col></Row>
            <Row><Col><MakeBChart make="make_year_count"/></Col></Row>
          </div>}
      </Row>
    )
  }
}

Dashboard.propTypes = {
  selectedMake: PropTypes.string.isRequired,
  d3: PropTypes.array.isRequired,
  isFetching: PropTypes.bool.isRequired,
  lastUpdated: PropTypes.number,
  dispatch: PropTypes.func.isRequired
}

function mapStateToProps(state) {
  const { selectedMake, d3ByMake } = state
  const {
    isFetching,
    lastUpdated,
    items: d3
  } = d3ByMake[selectedMake] || {
    isFetching: true,
    items: []
  }

  return {
    selectedMake,
    d3,
    isFetching,
    lastUpdated
  }
}

export default connect(mapStateToProps)(Dashboard)
