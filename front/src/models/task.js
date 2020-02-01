class Task {
    constructor({ name, id }) {
        this.name = name;
        this.id = id;
    }

    static comp(A, B) {
        return A.id - B.id;
    }
}

export default Task;
