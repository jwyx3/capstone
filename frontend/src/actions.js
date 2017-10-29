import axios from 'axios';

export const REQUEST_D3 = 'REQUEST_D3'
export const RECEIVE_D3 = 'RECEIVE_D3'
export const REQUEST_MAKES = 'REQUEST_MAKES'
export const RECEIVE_MAKES = 'RECEIVE_MAKES'
export const SELECT_MAKE = 'SELECT_MAKE'
export const INVALIDATE_MAKE = 'INVALIDATE_MAKE'


const apiClient = function() {
    const token = store.getState().token;
    const params = {
      baseURL: "http://localhost:3000"
    };
    return axios.create(params);
}

export function selectMake(make) {
  return {
    type: SELECT_MAKE,
    make
  }
}

export function invalidateMake(make) {
  return {
    type: INVALIDATE_MAKE,
    make
  }
}

function requestMakes() {
  return {
    type: REQUEST_MAKES
  }
}

function receiveMakes(json) {
  return {
    type: RECEIVE_MAKES,
    makes: json.data.results,
    receivedAt: Date.now()
  }
}

function requestD3(make) {
  return {
    type: REQUEST_D3,
    make
  }
}

function receiveD3(make, json) {
  return {
    type: RECEIVE_D3,
    make,
    d3: json.data.children.map(child => child.data),
    receivedAt: Date.now()
  }
}

function fetchMakes() {
  return dispatch => {
    dispatch(requestMakes())
    return apiClient().get('/makes/with_ads/', {
      params: {
        fields: 'name,url',
        limit: 0
      }
    })
    .then(response => response.json())
    .then(json => dispatch(receiveMakes(json)))
  }
}

function shouldFetchMakes(state) {
  const makes = state.makes
  if (!makes) {
    return true
  } else if (makes.isFetching) {
    return false
  } else {
    return makes.didInvalidate
  }
}

export function fetchMakesIfNeeded() {
  return (dispatch, getState) => {
    if (shouldFetchMakes(getState())) {
      return dispatch(fetchMakes())
    }
  }
}

function fetchD3(make) {
  return dispatch => {
    dispatch(requestD3(make))
    return axios.create({baseURL: URL})
    return fetch(`/static/d3/${make}.json`)
      .then(response => response.json())
      .then(json => dispatch(receiveD3(make, json)))
  }
}

function shouldFetchD3(state, make) {
  const d3 = state.d3ByMake[make]
  if (!d3) {
    return true
  } else if (d3.isFetching) {
    return false
  } else {
    return d3.didInvalidate
  }
}

export function fetchD3IfNeeded(make) {
  return (dispatch, getState) => {
    if (shouldFetchD3(getState(), make)) {
      return dispatch(fetchD3(make))
    }
  }
}
