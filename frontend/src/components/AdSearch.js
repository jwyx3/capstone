import { Table, FormControl, InputGroup } from 'react-bootstrap';
import React, { Component } from 'react';
import Client from '../util/ApiClient';
import _ from 'lodash';

class AdSearch extends Component {
  constructor(props) {
    super(props);

    this.state = {
      ads: [],
      showRemoveIcon: false,
      searchValue: ''
    };
  }

  handleSearchChange(event) {
    const self = this;
    const value = event.target.value;

    this.setState({
      searchValue: value
    });

    if (value === "") {
      this.setState({
        ads: [],
        showRemoveIcon: false
      });

    } else {
      this.setState({
        showRemoveIcon: true
      });

      Client.searchAds(value, (error, response) => {
        if (error) {
          console.log(error);
          return;
        }
        self.setState({
          ads: response.data.results
        });
      });
    }
  };

  handleSearchCancel() {
    this.setState({
      ads: [],
      showRemoveIcon: false,
      searchValue: ""
    });
  };

  render() {
    const { showRemoveIcon, ads } = this.state;
    const removeIconStyle = showRemoveIcon ? {} : { visibility: 'hidden' };

    const adRows = ads.map((ad, idx) => (
      <tr key={idx} onClick={() => this.props.onAdClick(ad)}>
        <td>{ad.title}</td>
        <td className="right aligned">
          <a href={ad.post_url} target="_blank">{ad.posted_at}</a>
        </td>
        <td className="right aligned">{ad.predict_price}</td>
      </tr>
    ));

    return (
      <Table responsive selectable>
        <thead>
          <tr>
            <th colSpan="5">
              <div className="fluid">
                <InputGroup bsSize="small">
                  <InputGroup.Addon>
                    <i className="glyphicon glyphicon-search"/>
                  </InputGroup.Addon>
                  <FormControl type="text"
                    placeholder="Search ads..."
                    value={this.state.searchValue}
                    onChange={this.handleSearchChange.bind(this)}/>
                  <InputGroup.Addon style={removeIconStyle}>
                    <i className="glyphicon glyphicon-remove"
                      onClick={this.handleSearchCancel.bind(this)}/>
                  </InputGroup.Addon>
                </InputGroup>
              </div>
            </th>
          </tr>
          <tr>
            <th className="eight wide">Description</th>
            <th>Posted Time</th>
            <th>Predicted Price</th>
          </tr>
        </thead>
        <tbody>
          {adRows}
        </tbody>
      </Table>
    );
  }
}

export default AdSearch;
