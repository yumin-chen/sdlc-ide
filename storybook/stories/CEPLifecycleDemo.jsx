import React from 'react';
import PropTypes from 'prop-types';

const CEPLifecycleDemo = ({ status }) => {
  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
      <h2>CEP Lifecycle Demo</h2>
      <p>Current Status: <strong>{status}</strong></p>
    </div>
  );
};

CEPLifecycleDemo.propTypes = {
  status: PropTypes.string.isRequired,
};

export default CEPLifecycleDemo;
