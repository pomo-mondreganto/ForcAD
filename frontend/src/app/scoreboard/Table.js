import React from 'react';

import styled from 'styled-components';
import { serviceColors } from 'config';

const TableCell = styled.div`
    border-bottom: 1px solid #c6cad1;
    align-self: stretch;
    display: grid;
    text-align: center;
    align-content: center;
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
    align-content: stretch;
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

const TeamTaskInfo = styled.div`
    display: grid;
    align-items: center;

    grid-template-columns: 1fr;
    grid-template-rows: repeat(3, 1fr);
`;

const TeamTaskInfoRow = styled.div`
    text-align: start;
    padding-left: 5px;
`;

const TeamTaskInfoComponent = ({
    stolen = null,
    lost = null,
    score = null,
    upRounds = null,
    round,
    init
}) => (
    <TeamTaskInfo>
        <TeamTaskInfoRow>
            <b>SLA: </b>
            {init ? '0.00%' : `${((100.0 * upRounds) / round).toFixed(2)}%`}
        </TeamTaskInfoRow>
        <TeamTaskInfoRow>
            <b>FP: </b>
            {init ? 0 : score.toFixed(2)}
        </TeamTaskInfoRow>
        <TeamTaskInfoRow>
            <b>F: </b>
            {init || (stolen === 0 && lost === 0) ? '0' : `+${stolen}/-${lost}`}
        </TeamTaskInfoRow>
    </TeamTaskInfo>
);

const TeamTaskComponent = ({
    status = null,
    last,
    message = null,
    stolen = null,
    lost = null,
    score = null,
    upRounds = null,
    round,
    init
}) => (
    <TeamTask status={init ? -1 : status} last={last}>
        <Tooltip>{init ? '' : message}</Tooltip>
        <TeamTaskInfoComponent
            stolen={stolen}
            lost={lost}
            score={score}
            upRounds={upRounds}
            round={round}
            init={init}
        />
    </TeamTask>
);

const TeamRow = ({ index, name, ip, score, tasks, round, init }) => (
    <>
        <TeamNumber>{index + 1}</TeamNumber>
        <TeamName>
            <div>{name}</div>
            <div>{ip}</div>
        </TeamName>
        <TeamScore>{init ? '' : score.toFixed(2)}</TeamScore>
        {tasks.map(
            (
                {
                    task_id: taskId,
                    message = null,
                    status = null,
                    stolen = null,
                    lost = null,
                    score: taskScore = null,
                    up_rounds: upRounds = null
                },
                taskIndex
            ) => (
                <TeamTaskComponent
                    key={taskId}
                    message={message}
                    status={status}
                    last={taskIndex + 1 === tasks.length}
                    stolen={stolen}
                    lost={lost}
                    score={taskScore}
                    upRounds={upRounds}
                    round={round}
                    init={init}
                />
            )
        )}
    </>
);

const TableComponent = ({ tasks, teams, round, init }) => (
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
            <TeamRow
                {...team}
                index={index}
                key={team.id}
                round={round}
                init={init}
            />
        ))}
    </Table>
);

export default TableComponent;
