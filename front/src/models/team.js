import TeamTask from '@/models/teamTask';

class Team {
    constructor({ name, ip, id, teamTasks }) {
        this.name = name;
        this.ip = ip;
        this.id = id;
        this.update(teamTasks);
    }

    update(teamTasks) {
        this.tasks = teamTasks
            .filter(({ team_id: teamId }) => teamId === this.id)
            .map(teamTask => new TeamTask(teamTask))
            .sort(TeamTask.comp);
        console.log(this.tasks);
        this.score = this.tasks.reduce((acc, { score }) => acc + score, 0);
    }

    static comp(A, B) {
        return B.score - A.score;
    }
}

export default Team;
