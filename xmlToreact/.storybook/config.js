import * as storybook from '@storybook/react';
import centered from '@storybook/addon-centered';
import { withKnobs } from '@storybook/addon-knobs/react';

// import initExtensions from './extensions';

storybook.addDecorator(centered);
storybook.addDecorator(withKnobs);

// initExtensions(storybook);

const req = require.context('../src', true, /.stories.tsx$/);
storybook.configure(() => {
  req.keys().forEach(filename => req(filename));
}, module);
