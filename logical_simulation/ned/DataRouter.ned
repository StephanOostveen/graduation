simple DataRouter {
    parameters:
        @display("i=block/process,blue");
        string busname;

    gates:
        input in[];
        output out[];
}