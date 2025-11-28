import React from 'react';
import PropTypes from 'prop-types';

const TemporalBuffer = ({ events }) => {
  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
      <h2>Temporal Buffer</h2>
      <ul>
        {events.map((event, index) => (
          <li key={index}>{event}</li>
        ))}
      </ul>
    </div>
  );
};

TemporalBuffer.propTypes = {
  events: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default TemporalBuffer;
