let url = '';

if (process.env.NODE_ENV === 'development') {
    url = 'http://127.0.0.1:8080';
} else {
    url = window.location.origin;
}

const serverUrl = url;

const statuses = [101, 102, 103, 104, 110];

const serviceStatuses = {
    101: 'UP',
    102: 'CORRUPT',
    103: 'MUMBLE',
    104: 'DOWN',
    '110': 'CHECK FAILED',
    '-1': 'OFFLINE'
};

const serviceColors = {
    101: '#7dfc74',
    102: '#5191ff',
    103: '#ff9114',
    104: '#ff5b5b',
    '110': '#ffff00',
    '-1': '#f142f477'
};

export { serverUrl, serviceColors, serviceStatuses, statuses };
