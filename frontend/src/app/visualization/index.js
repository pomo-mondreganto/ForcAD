import React from 'react';

import io from 'socket.io-client';
import { serverUrl } from 'config';
import axios from 'axios';
import Component from './Component';

class Visualization extends React.Component {
    constructor(props) {
        super(props);

        try {
            this.initSocket();
        } catch (e) {
            console.log(e);
        }

        this.state = {
            flags: [],
            teams: []
        };
    }

    async componentDidMount() {
        const response = await axios.get(`${serverUrl}/api/teams/`);
        const { data } = response;
        this.setState({ teams: data });
    }

    initSocket = () => {
        try {
            this.server = io(`${serverUrl}/api/sio_interface`, {
                forceNew: true
            });
        } catch (e) {
            throw new Error('Server is down');
        }

        this.server.on('flag_stolen', ({ data }) => {
            const json = JSON.parse(data);
            this.setState(({ teams, flags }) => {
                const newFlag = {
                    attacker: teams.filter(
                        team => team.id === json.attacker_id
                    )[0].name,
                    victim: teams.filter(team => team.id === json.victim_id)[0]
                        .name,
                    delta: json.attacker_delta
                };
                return { flags: flags.concat([newFlag]).slice(-100) };
            });
        });
    };

    render() {
        return <Component {...this.state} />;
    }
}

export default Visualization;
