function model = build_model()
% Build a reviewable basic-block model; no additional testing products needed.
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
model = 'cooling_fan';
folder = fullfile(root, 'models');
if ~exist(folder, 'dir'), mkdir(folder); end
target = fullfile(folder, [model '.slx']);
% Protect manual model edits: existing models are loaded, never overwritten.
if bdIsLoaded(model), return; end
if exist(target, 'file'), load_system(target); return; end
new_system(model);
set_param(model, 'SolverType','Fixed-step', 'Solver','FixedStepDiscrete', ...
    'FixedStep','0.01', 'StartTime','0', 'StopTime','0.5', ...
    'ReturnWorkspaceOutputs','on', 'SaveOutput','off', 'SaveTime','on');
ws = get_param(model, 'ModelWorkspace');
assignin(ws, 'FAN_ON_TEMP',95);
assignin(ws, 'FAN_OFF_TEMP',90);
assignin(ws, 'CONTROL_PERIOD',0.1);

add_block('simulink/Sources/In1',[model '/temperature'], ...
    'Port','1','OutDataTypeStr','double','SampleTime','0.01','Interpolate','off', ...
    'Position',[30 75 60 95]);
add_block('simulink/Sources/In1',[model '/sensor_valid'], ...
    'Port','2','OutDataTypeStr','boolean','SampleTime','0.01','Interpolate','off', ...
    'Position',[30 245 60 265]);
add_block('simulink/Discrete/Zero-Order Hold',[model '/TemperatureSample'], ...
    'SampleTime','CONTROL_PERIOD','Position',[100 65 155 105]);
add_block('simulink/Discrete/Zero-Order Hold',[model '/SensorSample'], ...
    'SampleTime','CONTROL_PERIOD','Position',[100 235 155 275]);
add_block('simulink/Logic and Bit Operations/Compare To Constant', ...
    [model '/AtOrAboveOn'],'relop','>=','const','FAN_ON_TEMP', ...
    'Position',[205 40 275 80]);
add_block('simulink/Logic and Bit Operations/Compare To Constant', ...
    [model '/AtOrBelowOff'],'relop','<=','const','FAN_OFF_TEMP', ...
    'Position',[205 135 275 175]);
add_block('simulink/Sources/Constant',[model '/True'],'Value','true', ...
    'OutDataTypeStr','boolean','Position',[300 5 335 25]);
add_block('simulink/Sources/Constant',[model '/False'],'Value','false', ...
    'OutDataTypeStr','boolean','Position',[300 100 335 120]);
add_block('simulink/Signal Routing/Switch',[model '/OffOrHold'], ...
    'Criteria','u2 ~= 0','Position',[375 120 410 190]);
add_block('simulink/Signal Routing/Switch',[model '/OnOrLower'], ...
    'Criteria','u2 ~= 0','Position',[460 25 495 95]);
add_block('simulink/Signal Routing/Switch',[model '/SensorOverride'], ...
    'Criteria','u2 ~= 0','Position',[550 180 585 250]);
add_block('simulink/Discrete/Unit Delay',[model '/PreviousFan'], ...
    'InitialCondition','false','SampleTime','CONTROL_PERIOD', ...
    'Position',[440 340 490 380]);
add_block('simulink/Logic and Bit Operations/Logical Operator',[model '/Fault'], ...
    'Operator','NOT','Position',[390 270 430 310]);
add_block('simulink/Sinks/Out1',[model '/fan_cmd'], ...
    'Port','1','Position',[710 205 740 225]);
add_block('simulink/Sinks/Out1',[model '/fault_flag'], ...
    'Port','2','Position',[710 285 740 305]);
for entry = {'FanLog','FaultLog'}
    name = entry{1};
    if strcmp(name,'FanLog'), ypos=145; variable='fan_log';
    else, ypos=325; variable='fault_log'; end
    add_block('simulink/Sinks/To Workspace',[model '/' name], ...
        'VariableName',variable,'SaveFormat','Timeseries','SampleTime','0.01', ...
        'MaxDataPoints','inf','Position',[660 ypos 750 ypos+30]);
end
connections = {
    'temperature/1','TemperatureSample/1';
    'sensor_valid/1','SensorSample/1';
    'TemperatureSample/1','AtOrAboveOn/1';
    'TemperatureSample/1','AtOrBelowOff/1';
    'False/1','OffOrHold/1';
    'AtOrBelowOff/1','OffOrHold/2';
    'PreviousFan/1','OffOrHold/3';
    'True/1','OnOrLower/1';
    'AtOrAboveOn/1','OnOrLower/2';
    'OffOrHold/1','OnOrLower/3';
    'OnOrLower/1','SensorOverride/1';
    'SensorSample/1','SensorOverride/2';
    'True/1','SensorOverride/3';
    'SensorOverride/1','PreviousFan/1';
    'SensorOverride/1','fan_cmd/1';
    'SensorOverride/1','FanLog/1';
    'SensorSample/1','Fault/1';
    'Fault/1','fault_flag/1';
    'Fault/1','FaultLog/1'};
for k=1:size(connections,1)
    add_line(model, connections{k,1}, connections{k,2}, 'autorouting','on');
end
note=Simulink.Annotation(model, 'Cooling fan: 100ms control / 10ms observation');
note.Position=[30 -40];
set_param(model,'SimulationCommand','update');
save_system(model,target);
end
