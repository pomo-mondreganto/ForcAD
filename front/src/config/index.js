let url = '';

if (import.meta.env.DEV) {
    url = 'http://127.0.0.1:8080';
} else {
    url = window.location.origin;
}

const serverUrl = url;
const apiUrl = `${serverUrl}/api`;

const statuses = [101, 102, 103, 104, 110];

const statusesNames = {
    101: 'UP',
    102: 'CORRUPT',
    103: 'MUMBLE',
    104: 'DOWN',
    110: 'CHECK FAILED',
    '-1': 'OFFLINE',
};

const statusColors = {
    101: '#7dfc74',
    102: '#5191ff',
    103: '#ff9114',
    104: '#ff5b5b',
    110: '#ffff00',
    '-1': '#fa83fc',
};

const defaultStatusColor = '#ffffff';

const topTeamColors = ['#ffdf00', '#c0c0c0', '#d3983f'];
const defaultTeamColor = '#ffffff';

export {
    serverUrl,
    apiUrl,
    statusesNames,
    statuses,
    topTeamColors,
    defaultTeamColor,
    statusColors,
    defaultStatusColor,
};
