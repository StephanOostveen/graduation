void cgw_task_50ms(void) {
    receive_task();
    authentication_task();
    exterior_lighting_50ms_task();
    transmit_task();
}