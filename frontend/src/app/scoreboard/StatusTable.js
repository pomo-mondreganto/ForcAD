import React from 'react';

import styled from 'styled-components';

import { statuses, serviceStatuses, serviceColors } from 'config';

const StatusCell = styled.div`
    background: ${props => serviceColors[props.status]};
    align-self: stretch;
    display: grid;
    align-content: center;
    text-align: center;
    padding-top: 7px;
    padding-bottom: 7px;
`;

const StatusTable = styled.div`
    display: grid;
    grid-template-columns: repeat(${statuses.length}, 1fr);
    margin-bottom: 30px;
`;

const statusTableComponent = () => (
    <StatusTable>
        {statuses.map((status, index) => (
            <StatusCell key={index} status={status}>
                {serviceStatuses[status]}
            </StatusCell>
        ))}
    </StatusTable>
);

export default statusTableComponent;
