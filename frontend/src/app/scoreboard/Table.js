import React from 'react';

import styled from 'styled-components';
import { serviceColors } from 'config';

const TableCell = styled.div`
    border-bottom: 1px solid #c6cad1;
    align-self: stretch;
    display: grid;
    align-content: center;
    text-align: center;
`;

const TableColumnHead = styled.div`
    text-align: center;
    padding: 10px;
    border-bottom: 1px solid #c6cad1;
    border-top: 1px solid #c6cad1;
    ${props => (props.first ? 'border-left: 1px solid #c6cad1;' : '')}
    ${props => (props.last ? 'border-right: 1px solid #c6cad1;' : '')}
`;

const Table = styled.div`
    display: grid;
    grid-template-columns: auto auto auto repeat(
            ${props => props.tasks_number},
            1fr
        );
    grid-template-rows: auto repeat(${props => props.teams_number}, 100px);
`;

const TeamNumber = styled(TableCell)`
    padding-left: 5px;
    padding-right: 5px;
    border-left: 1px solid #c6cad1;
`;

const TeamName = styled(TableCell)`
    min-width: 300px;
`;

const TeamScore = styled(TableCell)`
    padding-left: 20px;
    padding-right: 20px;
`;

const TeamTask = styled(TableCell)`
    background: ${props => serviceColors[props.status]};
    ${props => (props.last ? 'border-right: 1px solid #c6cad1;' : '')}
    position: relative;
`;

const Tooltip = styled.div`
    opacity: 0;
    background-color: #333333;
    color: #f3f3f3;
    position: absolute;
    width: 100%;
    height: 100%;

    display: grid;
    align-content: center;

    &:hover {
        opacity: 1;
    }
`;

const TeamRow = ({ index, name, ip, score, tasks }) => (
    <>
        <TeamNumber>{index + 1}</TeamNumber>
        <TeamName>
            <div>{name}</div>
            <div>{ip}</div>
        </TeamName>
        <TeamScore>{score}</TeamScore>
        {tasks.map(({ task_id: taskId, message, status }, taskIndex) => (
            <TeamTask
                key={taskId}
                status={status}
                last={taskIndex + 1 === tasks.length}
            >
                <Tooltip>{message}</Tooltip>
            </TeamTask>
        ))}
    </>
);

const TableComponent = ({ tasks, teams }) => (
    <Table tasks_number={tasks.length} teams_number={teams.length}>
        <TableColumnHead first>
            <b>#</b>
        </TableColumnHead>
        <TableColumnHead>
            <b>team</b>
        </TableColumnHead>
        <TableColumnHead>
            <b>score</b>
        </TableColumnHead>
        {tasks.map(({ id, name }, taskIndex) => (
            <TableColumnHead last={taskIndex + 1 === tasks.length} key={id}>
                <b>{name}</b>
            </TableColumnHead>
        ))}
        {teams.map((team, index) => (
            <TeamRow {...team} index={index} key={team.id} />
        ))}
    </Table>
);

export default TableComponent;
