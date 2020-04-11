import TeamTask from '@/models/teamTask';

class Team {
    constructor({ name, ip, id, teamTasks, highlighted }) {
        this.name = name;
        this.ip = ip;
        this.id = id;
        this.highlighted = highlighted;
        this.update(teamTasks);
    }

    update(teamTasks) {
        this.tasks = teamTasks
            .filter(({ team_id: teamId }) => teamId === this.id)
            .map(teamTask => new TeamTask(teamTask))
            .sort(TeamTask.comp);
        this.score = this.tasks.reduce(
            (acc, { score, sla }) => acc + score * (sla / 100.0),
            0
        );
    }

    static comp(A, B) {
        return B.score - A.score;
    }
}

export default Team;
