function check_model()
% Configuration checks, not a certified static analysis or a proof of behavior.
root=fileparts(fileparts(fileparts(mfilename('fullpath'))));
model=build_model();
cleanup=onCleanup(@() close_system(model,0)); %#ok<NASGU>
names={'fan_initial_false','state_period','temperature_period','sensor_period', ...
       'temperature_double','sensor_boolean','on_comparison','off_comparison', ...
       'final_fan_feedback','fault_has_no_memory','temperature_parameter', ...
       'off_parameter','control_parameter','solver_step','first_evaluation'};
passed=false(size(names));
passed(1)=strcmp(get_param([model '/PreviousFan'],'InitialCondition'),'false');
passed(2)=strcmp(get_param([model '/PreviousFan'],'SampleTime'),'CONTROL_PERIOD');
passed(3)=strcmp(get_param([model '/TemperatureSample'],'SampleTime'),'CONTROL_PERIOD');
passed(4)=strcmp(get_param([model '/SensorSample'],'SampleTime'),'CONTROL_PERIOD');
passed(5)=strcmp(get_param([model '/temperature'],'OutDataTypeStr'),'double');
passed(6)=strcmp(get_param([model '/sensor_valid'],'OutDataTypeStr'),'boolean');
passed(7)=strcmp(get_param([model '/AtOrAboveOn'],'relop'),'>=');
passed(8)=strcmp(get_param([model '/AtOrBelowOff'],'relop'),'<=');
ports=get_param([model '/PreviousFan'],'PortHandles');
line=get_param(ports.Inport,'Line');
source=get_param(line,'SrcBlockHandle');
passed(9)=strcmp(getfullname(source),[model '/SensorOverride']);
passed(10)=strcmp(get_param([model '/Fault'],'Operator'),'NOT');
ws=get_param(model,'ModelWorkspace');
passed(11)=getVariable(ws,'FAN_ON_TEMP')==95;
passed(12)=getVariable(ws,'FAN_OFF_TEMP')==90;
passed(13)=getVariable(ws,'CONTROL_PERIOD')==0.1;
passed(14)=strcmp(get_param(model,'Solver'),'FixedStepDiscrete') && ...
    str2double(get_param(model,'FixedStep'))==0.01;
passed(15)=str2double(get_param(model,'StartTime'))==0;
folder=fullfile(root,'results');
if ~exist(folder,'dir'), mkdir(folder); end
writetable(table(names(:),passed(:),'VariableNames',{'check','passed'}), ...
    fullfile(folder,'model-configuration-checks.csv'));
assert(all(passed),'Model configuration check failed');
set_param(model,'SimulationCommand','update');
fprintf('Model configuration: %d/%d checks passed\n',sum(passed),numel(passed));
% Reviewable overview. Failure to render must not affect simulation results.
figures=fullfile(folder,'figures');
if ~exist(figures,'dir'), mkdir(figures); end
print(['-s' model],'-dpng',fullfile(figures,'model.png'));
end
