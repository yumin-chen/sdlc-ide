import React from 'react';
import NFAInstance from './NFAInstance';

export default {
  title: 'CEP Components/NFAInstance',
  component: NFAInstance,
};

const Template = (args) => <NFAInstance {...args} />;

export const PartialMatch = Template.bind({});
PartialMatch.args = {
  state: 'PartialMatch',
  matchedEvents: ['Event A'],
};

export const CompletedMatch = Template.bind({});
CompletedMatch.args = {
  state: 'Completed',
  matchedEvents: ['Event A', 'Event B', 'Event C'],
};
