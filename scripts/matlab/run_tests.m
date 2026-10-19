function run_tests(variant)
% Execute real Simulink simulations; variant changes are in-memory only.
if nargin < 1, variant = 'baseline'; end
allowed = {'baseline','on_strict','wrong_feedback','no_override'};
assert(ismember(variant,allowed),'Unknown variant');
root = fileparts(fileparts(fileparts(mfilename('fullpath'))));
model = build_model();
cleanup = onCleanup(@() close_system(model,0)); %#ok<NASGU>
manifest = jsondecode(fileread(fullfile(root,'tests','manifest.json')));
if strcmp(variant,'baseline'), folder=fullfile(root,'results','actual');
else, folder=fullfile(root,'results','mutations',variant); end
if ~exist(folder,'dir'), mkdir(folder); end
% Remove prior CSVs for this run so failed simulations cannot reuse old results.
for k=1:numel(manifest)
    output = fullfile(folder,[manifest(k).id '.csv']);
    if exist(output,'file'), delete(output); end
end
env = struct('matlab',version,'products',{ver},'variant',variant, ...
    'timestamp',char(datetime('now','TimeZone','UTC','Format','yyyy-MM-dd''T''HH:mm:ssXXX')));
fid=fopen(fullfile(folder,'environment.json'),'w');
assert(fid~=-1,'Cannot write environment');
fprintf(fid,'%s\n',jsonencode(env)); fclose(fid);
for k=1:numel(manifest)
    id=manifest(k).id;
    input=readtable(fullfile(root,'tests','inputs',[id '.csv']));
    temp=timeseries(input.temperature,input.time);
    temp=setinterpmethod(temp,'zoh');
    valid=timeseries(logical(input.sensor_valid),input.time);
    valid=setinterpmethod(valid,'zoh');
    data=Simulink.SimulationData.Dataset;
    data=data.addElement(temp,'temperature');
    data=data.addElement(valid,'sensor_valid');
    simin=Simulink.SimulationInput(model);
    simin=simin.setExternalInput(data);
    simin=simin.setModelParameter('StopTime',num2str(manifest(k).stop_time,17));
    if strcmp(variant,'on_strict')
        simin=simin.setBlockParameter([model '/AtOrAboveOn'],'relop','>');
    elseif strcmp(variant,'wrong_feedback')
        % Equivalent fault: previous state ignores the forced fan ON on sensor error.
        delete_line(model,'SensorOverride/1','PreviousFan/1');
        add_line(model,'OnOrLower/1','PreviousFan/1');
    elseif strcmp(variant,'no_override')
        % Ignore sensor error and always use the normal temperature command.
        delete_line(model,'True/1','SensorOverride/3');
        add_line(model,'OnOrLower/1','SensorOverride/3');
    end
    out=sim(simin);
    fan=out.get('fan_log'); fault=out.get('fault_log');
    assert(isequal(fan.Time,fault.Time),'Output timestamps differ');
    result=table(fan.Time,double(fan.Data(:)),double(fault.Data(:)), ...
        'VariableNames',{'time','fan_cmd','fault_flag'});
    writetable(result,fullfile(folder,[id '.csv']));
    fprintf('%s %s simulated\n',variant,id);
    if strcmp(variant,'wrong_feedback')
        delete_line(model,'OnOrLower/1','PreviousFan/1');
        add_line(model,'SensorOverride/1','PreviousFan/1');
    elseif strcmp(variant,'no_override')
        delete_line(model,'OnOrLower/1','SensorOverride/3');
        add_line(model,'True/1','SensorOverride/3');
    end
end
end
