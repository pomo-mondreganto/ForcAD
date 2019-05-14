import React from 'react';

import styled, { createGlobalStyle } from 'styled-components';

import TableComponent from './Table';
import StatusesComponent from './StatusTable';
import NavbarComponent from './Navbar';

const GlobalStyle = createGlobalStyle`
    html, body {
        margin: 0;
        padding: 0;
        font-family: 'Merriweather', serif;
    }
`;

const Page = styled.div`
    padding-left: 5%;
    padding-right: 5%;
`;

const Component = ({ ok, tasks, teams, round }) => {
    if (!ok) {
        return null;
    }

    return (
        <>
            <GlobalStyle />
            <NavbarComponent round={round} />
            <Page>
                <StatusesComponent />
                <TableComponent tasks={tasks} teams={teams} round={round} />
            </Page>
        </>
    );
};

export default Component;
