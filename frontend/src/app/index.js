import React from 'react';
import { Route, Switch } from 'react-router-dom';

import Scoreboard from './scoreboard';
import Visualization from './visualization';

const App = () => (
    <Switch>
        <Route component={Scoreboard} path="/" exact />
        <Route component={Visualization} path="/v/" exact />
    </Switch>
);

export default App;
