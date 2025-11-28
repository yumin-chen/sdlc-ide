import React from 'react';
import TemporalBuffer from './TemporalBuffer';

export default {
  title: 'CEP Components/TemporalBuffer',
  component: TemporalBuffer,
};

const Template = (args) => <TemporalBuffer {...args} />;

export const Empty = Template.bind({});
Empty.args = {
  events: [],
};

export const WithEvents = Template.bind({});
WithEvents.args = {
  events: ['Event A', 'Event B', 'Event C'],
};
