import React from 'react';
import { Route, Switch } from 'react-router-dom';

import Scoreboard from './scoreboard';

const App = () => (
    <Switch>
        <Route component={Scoreboard} path="/" exact />
    </Switch>
);

export default App;
