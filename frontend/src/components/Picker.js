import { Form, FormGroup, FormControl, InputGroup } from 'react-bootstrap'
import { parseId } from '../util'
import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { fetchMakesIfNeeded } from '../actions'
import _ from 'lodash'

export default class Picker extends Component {
  renderOptions(options) {
    return options.map(option => {
      const id = parseId(option.url);
      const name = _.startCase(option.name);
      return (
        <option key={id} value={id}>{name}</option>
      );
    });
  }

  componentDidMount() {
    const { dispatch } = this.props
    dispatch(fetchMakesIfNeeded())
  }

  render() {
    const { value, onChange, options } = this.props;

    return (
      <Form inline>
        <FormGroup controlId="Make">
          <InputGroup bsSize="small">
            <InputGroup.Addon>Make</InputGroup.Addon>
            <FormControl componentClass="select"
              onChange={e => onChange(e.target.value)} value={value}>
              {this.renderOptions(options)}
            </FormControl>
          </InputGroup>
        </FormGroup>
      </Form>
    )
  }
}

Picker.propTypes = {
  options: PropTypes.arrayOf(PropTypes.string.isRequired).isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired
}
