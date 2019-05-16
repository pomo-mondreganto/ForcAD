let url = '';

if (process.env.NODE_ENV === 'development') {
    url = 'http://127.0.0.1:5002';
} else {
    url = window.location.origin;
}

const serverUrl = url;

const statuses = [101, 102, 103, 104, -1337];

const serviceStatuses = {
    101: 'UP',
    102: 'MUMBLE',
    103: 'CORRUPT',
    104: 'DOWN',
    '-1337': 'CHECK FAILED',
    '-1': 'OFFLINE'
};

const serviceColors = {
    101: '#7dfc74',
    102: '#ff9114',
    103: '#5191ff',
    104: '#ff5b5b',
    '-1337': '#ffff00',
    '-1': '#f142f477'
};

export { serverUrl, serviceColors, serviceStatuses, statuses };
