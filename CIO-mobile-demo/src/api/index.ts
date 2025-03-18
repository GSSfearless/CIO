import api from './client';
import authApi from './auth';
import queryApi from './query';
import focusPointApi from './focusPoint';
import sourceApi from './source';

export {
  api,
  authApi,
  queryApi,
  focusPointApi,
  sourceApi,
};

export default {
  api,
  auth: authApi,
  query: queryApi,
  focusPoint: focusPointApi,
  source: sourceApi,
}; 