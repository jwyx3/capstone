import { combineReducers } from 'redux'
import {
  SELECT_MAKE,
  INVALIDATE_MAKE,
  REQUEST_D3,
  RECEIVE_D3
} from './actions'

function selectedMake(state = 'Toyota', action) {
  switch (action.type) {
    case SELECT_MAKE:
      return action.make
    default:
      return state
  }
}

function d3(
  state = {
    isFetching: false,
    didInvalidate: false,
    items: []
  },
  action
) {
  switch (action.type) {
    case INVALIDATE_MAKE:
      return Object.assign({}, state, {
        didInvalidate: true
      })
    case REQUEST_D3:
      return Object.assign({}, state, {
        isFetching: true,
        didInvalidate: false
      })
    case RECEIVE_D3:
      return Object.assign({}, state, {
        isFetching: false,
        didInvalidate: false,
        items: action.d3,
        lastUpdated: action.receivedAt
      })
    default:
      return state
  }
}

function d3ByMake(state = {}, action) {
  switch (action.type) {
    case INVALIDATE_MAKE:
    case RECEIVE_D3:
    case REQUEST_D3:
      return Object.assign({}, state, {
        [action.make]: d3(state[action.make], action)
      })
    default:
      return state
  }
}

const rootReducer = combineReducers({
  d3ByMake,
  selectedMake
})

export default rootReducer
