network ExteriorLighting {
    submodules:
        cgw_exl_runnable: Runnable;
        scu_exl_runnable: Runnable;
        // scu_vpc_runnable: Runnable { @display("i=block/process,cyan");};
        vcu_exl_runnable: Runnable;
        // vcu_dcm_runnable: Runnable { @display("i=block/process,cyan");};
        
        operating_mode_lighting: DataDictionary;
        exterior_lighting_request: DataDictionary;
        fog_light_request: DataDictionary;
        fog_lights_active: DataDictionary;
        active_gear: DataDictionary;

        brake_lights_request: DataDictionary;

        turn_indication_request: DataDictionary;
        hazard_lights_request: DataDictionary;
        high_beam_request: DataDictionary;
        safety_hazard_lights_request: DataDictionary;
        ext_light_hmi_scenario: DataDictionary;
        ivi_headlight_level_setting: DataDictionary;
        actual_headlight_level: DataDictionary;
        closure_blink_request: DataDictionary;


        connections allowunconnected:
        //cgw connections
        cgw_exl_runnable.InterfaceInput++ <--> operating_mode_lighting.get++;
        cgw_exl_runnable.InterfaceInput++ <--> exterior_lighting_request.get++;
        cgw_exl_runnable.InterfaceInput++ <--> fog_light_request.get++;
        cgw_exl_runnable.InterfaceInput++ <--> active_gear.get++;

        //scu connections
        scu_exl_runnable.InterfaceInput++ <--> operating_mode_lighting.get++;
        scu_exl_runnable.InterfaceInput++ <--> brake_lights_request.get++;

        //vcu connections
        vcu_exl_runnable.InterfaceInput++ <--> operating_mode_lighting.get++;
        vcu_exl_runnable.InterfaceInput++ <--> turn_indication_request.get++;
        vcu_exl_runnable.InterfaceInput++ <--> hazard_lights_request.get++;
        vcu_exl_runnable.InterfaceInput++ <--> exterior_lighting_request.get++;
        vcu_exl_runnable.InterfaceInput++ <--> high_beam_request.get++;
        vcu_exl_runnable.InterfaceInput++ <--> fog_lights_active.get++;
        vcu_exl_runnable.InterfaceInput++ <--> safety_hazard_lights_request.get++;
        
        vcu_exl_runnable.InterfaceInput++ <--> ivi_headlight_level_setting.get++;
        vcu_exl_runnable.InterfaceInput++ <--> closure_blink_request.get++;

        cgw_exl_runnable.InterfaceOutput++ --> {@display("ls=green,2");} --> fog_lights_active.set;
        vcu_exl_runnable.InterfaceOutput++ --> {@display("ls=green,2");} --> ext_light_hmi_scenario.set;
        vcu_exl_runnable.InterfaceOutput++ --> {@display("ls=green,2");} --> actual_headlight_level.set;
        // scu_vpc_runnable.InterfaceOutput++ --> {@display("ls=green,2");} --> operating_mode_lighting.set;
        // vcu_dcm_runnable.InterfaceOutput++ --> {@display("ls=green,2");} --> exterior_lighting_request.set;
}