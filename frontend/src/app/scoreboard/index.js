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
            round: 0,
            tasks: null,
            teams: null
        };
    }

    getTeamsWithScoreSorted = (teams, teamTasks, round) => {
        console.log(teams);
        console.log(teams
            .map(team => ({
                ...team,
                tasks: teamTasks
                    .filter(teamTask => teamTask.team_id === team.id)
                    .sort((a, b) => a.id < b.id),
                score: teamTasks
                    .filter(teamTask => teamTask.team_id === team.id)
                    .reduce((acc, { score, up_rounds: upRounds }) => acc + score * upRounds / round, 0)
            })));
        console.log(teamTasks);
        console.log(round);
        return teams
            .map(team => ({
                ...team,
                tasks: teamTasks
                    .filter(teamTask => teamTask.team_id === team.id)
                    .sort((a, b) => a.id < b.id),
                score: teamTasks
                    .filter(teamTask => teamTask.team_id === team.id)
                    .reduce((acc, { score, up_rounds: upRounds }) => acc + score * upRounds / round, 0)
            }))
            .sort((a, b) => a.score < b.score || Math.abs(a.score - b.score) < 1e-5 && a.id > b.id);
    };

    initSocket = () => {
        try {
            this.server = io(`${serverUrl}/test`, { forceNew: true });
        } catch (e) {
            throw new Error('Server is down');
        }
        this.server.on('init_scoreboard', ({ data }) => {
            const json = JSON.parse(data);
            // console.log(json);
            const { state, tasks, teams } = json;

            this.setState({
                ok: true,
                round: state.round,
                tasks,
                teams: this.getTeamsWithScoreSorted(teams, state.team_tasks, state.round)
            });
        });
        this.server.on('update_scoreboard', ({ data }) => {
            const json = JSON.parse(data);
            // console.log(json);
            this.setState(({ teams }) => ({
                round: json.round,
                teams: this.getTeamsWithScoreSorted(teams, json.team_tasks, json.round)
            }));
        });
    };

    render() {
        return <Component {...this.state} />;
    }
}

export default Scoreboard;
