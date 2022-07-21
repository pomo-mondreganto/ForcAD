import TeamTask from '@/models/teamTask';

class Team {
    constructor({ name, ip, id, teamTasks, tasks, highlighted }) {
        this.name = name;
        this.ip = ip;
        this.id = id;
        this.highlighted = highlighted;
        this.taskModels = tasks;
        this.update(teamTasks);
    }

    update(teamTasks) {
        this.tasks = teamTasks.filter(({ teamId }) => teamId === this.id);
        this.score = this.tasks.reduce(
            (acc, { score, sla }) => acc + score * (sla / 100.0),
            0
        );
        let taskIds = this.tasks.map((x) => x.taskId);
        for (let task of this.taskModels) {
            if (!taskIds.includes(task.id)) {
                this.tasks.push(
                    new TeamTask({
                        id: 0,
                        task_id: task.id,
                        team_id: this.id,
                        status: 0,
                        stolen: 0,
                        lost: 0,
                        score: 0,
                        checks: 0,
                        checks_passed: 0,
                    })
                );
            }
        }
        this.tasks.sort(TeamTask.comp);
    }

    static comp(A, B) {
        return B.score - A.score;
    }
}

export default Team;
