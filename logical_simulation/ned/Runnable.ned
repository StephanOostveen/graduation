simple Runnable {
    parameters:
        @display("i=block/process,purple");
        string physical;
        string logical;
        string task;
        int period;
    gates:
        output InterfaceOutput[];
        inout InterfaceInput[];
}