import React from 'react';
import CEPLifecycleDemo from './CEPLifecycleDemo';

export default {
  title: 'CEP Demos/CEPLifecycleDemo',
  component: CEPLifecycleDemo,
};

const Template = (args) => <CEPLifecycleDemo {...args} />;

export const Default = Template.bind({});
Default.args = {
  status: 'Idle',
};

export const Processing = Template.bind({});
Processing.args = {
  status: 'Processing Event',
};

export const MatchFound = Template.bind({});
MatchFound.args = {
  status: 'Pattern Match Found',
};
