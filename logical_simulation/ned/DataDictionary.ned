simple DataDictionary {
    parameters:
        @display("i=block/process,grey");
        string datatype;
        bool reliability;
    gates:
        inout get[];
        input set;
}