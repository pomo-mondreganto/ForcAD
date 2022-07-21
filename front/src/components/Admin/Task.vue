<template>
    <form-wrapper
        v-if="task !== null"
        :title="message"
        :submit-callback="submitForm"
    >
        <p>
            Name:
            <input v-model="task.name" type="text" />
        </p>
        <p>
            Checker:
            <input v-model="task.checker" type="text" />
        </p>
        <p>
            Gets:
            <input v-model="task.gets" type="number" />
        </p>
        <p>
            Puts:
            <input v-model="task.puts" type="number" />
        </p>
        <p>
            Places:
            <input v-model="task.places" type="number" />
        </p>
        <p>
            Checker timeout:
            <input v-model="task.checker_timeout" type="number" />
        </p>
        <p>
            Checker type:
            <input v-model="task.checker_type" type="text" />
        </p>
        <p>
            Env path:
            <input v-model="task.env_path" type="text" />
        </p>
        <p>
            Get period:
            <input v-model="task.get_period" type="number" />
        </p>
        <p>
            Default score:
            <input v-model="task.default_score" type="number" />
        </p>
        <p>
            Active:
            <input
                type="checkbox"
                :checked="task.active"
                @input="task.active = $event.target.checked"
            />
        </p>
    </form-wrapper>
</template>

<script>
import FormWrapper from '@/components/Lib/FormWrapper.vue';

export default {
    components: { FormWrapper },

    data: function() {
        return {
            task: null,
            taskId: null,
            message: null,
        };
    },

    watch: {
        $route: async function() {
            await this.updateData();
        },
    },

    created: async function() {
        await this.updateData();
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
                    `/admin/tasks/${this.taskId}/`
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
