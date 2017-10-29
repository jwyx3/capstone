import axios from 'axios';
import store from '../store';
import { URL } from '../config/Api';
import _ from 'lodash';

export const apiClient = function() {
    const token = store.getState().token;
    const params = {
        baseURL: URL,
        headers: {'Authorization': 'Token ' + token}
    };
    return axios.create(params);
}

export const parseId = function(url) {
  url = _.trimEnd(url, '/')
  return url.substring(_.lastIndexOf(url, '/') + 1);
}

function searchAds(query, cb, limit = 100) {
  apiClient().get('/ads/', {
    params: {
      search: query,
      limit: limit,
    }
  })
  .then(function (response) {
    cb(null, response);
  })
  .catch(function (error) {
    cb(error);
  });
}

function recentAds(cb) {
  apiClient().get('/ads/')
  .then(function (response) {
    cb(null, response);
  })
  .catch(function (error) {
    cb(error);
  });
}

function usedMakes(cb) {
  apiClient().get('/makes/with_ads/', {
    params: {
      fields: 'name,url',
      limit: 0
    }
  })
  .then(function (response) {
    cb(null, response);
  })
  .catch(function (error) {
    cb(error);
  });
}

const Client = { searchAds, recentAds, usedMakes };
export default Client;
