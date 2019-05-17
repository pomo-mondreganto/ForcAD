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
        const data = await axios.get(`${serverUrl}/api/teams/`);
        console.log(data);
    }

    initSocket = () => {
        try {
            this.server = io(`${serverUrl}/api/sio_interface`, {
                forceNew: true
            });
        } catch (e) {
            throw new Error('Server is down');
        }

        // this.server.on('flag_stolen', ({ data }) => {
        //     const json = JSON.parse(data);
        //     console.log(json);
        //     this.setState(({ flags }) => {
        //         const newFlags = flags.concat([]);
        //     });
        // });
    };

    render() {
        return <Component {...this.state} />;
    }
}

export default Visualization;
