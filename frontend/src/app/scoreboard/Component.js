import React from 'react';

import styled from 'styled-components';

import TableComponent from './Table';
import StatusesComponent from './StatusTable';

const Page = styled.div`
    padding-left: 5%;
    padding-right: 5%;
    font-family: 'Merriweather', serif;
`;

const Component = ({ ok, tasks, teams }) => {
    if (!ok) {
        return null;
    }

    return (
        <Page>
            <StatusesComponent />
            <TableComponent tasks={tasks} teams={teams} />
        </Page>
    );
};

export default Component;
