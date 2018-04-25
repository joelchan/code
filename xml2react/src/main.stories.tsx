import * as React from 'react';
import { storiesOf } from '@storybook/react';
import { action } from '@storybook/addon-actions';
import {Reader1} from './reader1'
import {getTextFromXML} from './xml';
var {pText, imgsCaptions} = getTextFromXML();


storiesOf('Button', module)
  .add('with text', () => (
    <Reader1 text={pText} />
  ))
  .add('with some emoji', () => (
    <div onClick={action('clicked')}><span role="img" aria-label="so cool">😀 😎 👍 💯</span></div>
  ));   