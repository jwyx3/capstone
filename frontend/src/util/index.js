import _ from 'lodash';

export const parseId = function(url) {
  url = _.trimEnd(url, '/')
  return url.substring(_.lastIndexOf(url, '/') + 1);
}
