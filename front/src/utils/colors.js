import {
    statusColors,
    defaultStatusColor,
    topTeamColors,
    defaultTeamColor,
} from '@/config';

function getTeamRowBackground(index) {
    return index < topTeamColors.length
        ? topTeamColors[index]
        : defaultTeamColor;
}

function getTeamTaskBackground(status) {
    return statusColors[status] ? statusColors[status] : defaultStatusColor;
}

export { getTeamRowBackground, getTeamTaskBackground };
