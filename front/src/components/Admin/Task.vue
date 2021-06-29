<template>
    <form-wrapper
        v-if="task !== null"
        :title="message"
        :submitCallback="submitForm"
    >
        <p>
            Name:
            <input type="text" v-model="task.name" />
        </p>
        <p>
            Checker:
            <input type="text" v-model="task.checker" />
        </p>
        <p>
            Gets:
            <input type="number" v-model="task.gets" />
        </p>
        <p>
            Puts:
            <input type="number" v-model="task.puts" />
        </p>
        <p>
            Places:
            <input type="number" v-model="task.places" />
        </p>
        <p>
            Checker timeout:
            <input type="number" v-model="task.checker_timeout" />
        </p>
        <p>
            Checker type:
            <input type="text" v-model="task.checker_type" />
        </p>
        <p>
            Env path:
            <input type="text" v-model="task.env_path" />
        </p>
        <p>
            Get period:
            <input type="number" v-model="task.get_period" />
        </p>
        <p>
            Default score:
            <input type="number" v-model="task.default_score" />
        </p>
        <p>
            Active:
            <input
                type="checkbox"
                @input="task.active = $event.target.checked"
                :checked="task.active"
            />
        </p>
    </form-wrapper>
</template>

<script>
import FormWrapper from '@/components/Lib/FormWrapper';

export default {
    components: { FormWrapper },

    data: function() {
        return {
            task: null,
            taskId: null,
            message: null,
        };
    },

    created: async function() {
        await this.updateData();
    },

    watch: {
        $route: async function() {
            await this.updateData();
        },
    },

    methods: {
        updateData: async function() {
            this.taskId = this.$route.params.id;
            if (!this.taskId) {
                this.task = {
                    name: '',
                    checker: '',
                    gets: 1,
                    puts: 1,
                    places: 1,
                    checker_timeout: 20,
                    checker_type: 'hackerdom',
                    env_path: '',
                    get_period: 10,
                    default_score: 2500,
                    active: true,
                };
                this.message = 'Creating task';
            } else {
                const { data: task } = await this.$http.get(
                    `/admin/tasks/${this.taskId}`
                );
                this.task = task;
                this.message = `Editing task ${this.task.name} (${this.task.id})`;
            }
        },
        submitForm: async function() {
            if (!this.taskId) {
                const { data: task } = await this.$http.post(
                    '/admin/tasks/',
                    this.task
                );
                this.$router
                    .push({ name: 'taskAdmin', params: { id: task.id } })
                    .catch(() => {});
            } else {
                const { data: task } = await this.$http.put(
                    `/admin/tasks/${this.taskId}/`,
                    this.task
                );
                this.task = task;
                await this.updateData();
            }
        },
    },
};
</script>

<style lang="scss" scoped></style>
