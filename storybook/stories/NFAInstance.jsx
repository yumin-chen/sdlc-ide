import React from 'react';
import PropTypes from 'prop-types';

const NFAInstance = ({ state, matchedEvents }) => {
  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
      <h2>NFA Instance</h2>
      <p>Current State: <strong>{state}</strong></p>
      <p>Matched Events:</p>
      <ul>
        {matchedEvents.map((event, index) => (
          <li key={index}>{event}</li>
        ))}
      </ul>
    </div>
  );
};

NFAInstance.propTypes = {
  state: PropTypes.string.isRequired,
  matchedEvents: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default NFAInstance;
