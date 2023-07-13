function [s_out bad_flds] = validate_sfields(s_in,valid_flds,var_nm)
% VALIDATE_SFIELDS identifies and removes unexpected struct fields
%
% Intended use of this function is to validate struct input arguments
% to functions, such as configuration settings, where there is a strong
% likelihood of misspellings that might otherwise go undetected
%
% Input Params:
%  s_in         (struct) structure to be tested
%  valid_flds (1xN cell) cell array of valid field name strings (char arrays)
%                        Ex: {'Name', 'Address', 'email'}
%
%  var_nm          (str) var name of structure being tested, used to issue a
%                        generic warning message that includes the var name
%                        and the list of invalid field names, set to empty
%                        string ('', DEFAULT) to not issue warning
%
% Returns:
%  s_out (struct) copy of s_in with invalid fields removed
%  bad_flds (1xM cell) cell array of invalid field names found in s_in
%
% [s_out bad_flds] = VALIDATE_SFIELDS(s_in,valid_flds[,var_nm])
%
% COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.

if ~exist('var_nm','var') var_nm = []; end

if ~isstruct(s_in)
  error('validate_sfields:badInput', ...
        'First argument (s_in) needs to be a structure');
end

if ~iscell(valid_flds)
  error('validate_sfields:badInput', ...
    ['Second argument (valid_flds) needs to be a cell array of field ' ...
     'name strings (char arrays)']);
end

if ~isempty(var_nm) && ~ischar(var_nm)
  error('validate_sfields:badInput', ...
        'Third argument (var_nm) must be empty or a string (char array)');
end

% build set of valid field names for quick checking
vflds = containers.Map();  % will use as a set container, values ignored
for ifld = 1:length(valid_flds)
  fld0 = valid_flds{ifld};
  if ~ischar(fld0)
    error('validate_sfields:badInput', ...
          ['valid_flds cell array argument contains a cell element that ' ...
           'is not a char array string']);
  end
  vflds(fld0) = [];  % only store the key, used as a set container
end

flds_in = fieldnames(s_in);
Nbad = 0;
bad_flds = cell(0);
s_out = struct;
for ifld = 1:length(flds_in)
  fld0 = flds_in{ifld};
  if vflds.isKey(fld0)
    s_out.(fld0) = s_in.(fld0);
  else
    Nbad = Nbad + 1;
    bad_flds{Nbad} = fld0;
  end
end

if ~isempty(var_nm) && Nbad > 0
  msg = [var_nm ' has unexpected struct field names:'];
  for ifld = 1:Nbad
    msg0 = sprintf('\n  .%s',bad_flds{ifld});
    msg = [msg msg0];
  end
  warning(msg);
end

end  % validate_sfields
