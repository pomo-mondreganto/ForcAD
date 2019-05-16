import React from 'react';

import io from 'socket.io-client';
import { serverUrl } from 'config';
import Component from './Component';

class Scoreboard extends React.Component {
    constructor(props) {
        super(props);

        try {
            this.initSocket();
        } catch (e) {
            console.log(e);
        }

        this.state = {
            ok: false,
            init: false,
            round: 0,
            tasks: null,
            teams: null
        };
    }

    getTeamsWithScoreSorted = (teams, teamTasks, round) => {
        return teams
            .map(team => ({
                ...team,
                tasks: teamTasks
                    .filter(teamTask => teamTask.team_id === team.id)
                    .sort((a, b) => a.id < b.id),
                score: teamTasks
                    .filter(teamTask => teamTask.team_id === team.id)
                    .reduce(
                        (acc, { score, up_rounds: upRounds }) =>
                            acc + (score * upRounds) / round,
                        0
                    )
            }))
            .sort(
                (a, b) =>
                    a.score < b.score ||
                    (Math.abs(a.score - b.score) < 1e-5 && a.id > b.id)
            );
    };

    mapTasksWithTeams = (teams, tasks) => {
        return teams.map(team => ({
            ...team,
            tasks: tasks.map(task => ({ task_id: task.id }))
        }));
    };

    initSocket = () => {
        try {
            this.server = io(`${serverUrl}/test`, { forceNew: true });
        } catch (e) {
            throw new Error('Server is down');
        }
        this.server.on('init_scoreboard', ({ data }) => {
            const json = JSON.parse(data);
            const { tasks, teams } = json;

            console.log(json);

            this.setState({
                ok: true,
                init: true,
                tasks,
                teams: this.mapTasksWithTeams(teams, tasks),
                round: -1
            });
        });
        this.server.on('update_scoreboard', ({ data }) => {
            const json = JSON.parse(data);
            this.setState(({ teams }) => ({
                ok: true,
                init: false,
                round: json.round,
                teams: this.getTeamsWithScoreSorted(
                    teams,
                    json.team_tasks,
                    json.round
                )
            }));
        });
    };

    render() {
        return <Component {...this.state} />;
    }
}

export default Scoreboard;
