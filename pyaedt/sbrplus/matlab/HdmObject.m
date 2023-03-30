classdef HdmObject < handle
% HDMOBJECT is a generic handle container for the contents of an 'object'
% within a Heterogeneous Data Message (HDM).
%
% HDMOBJECT contains a single property, hdmObj, a public structure. The
% structure fields of hdmObj are not predefined and are determined entirely
% by the requirements of the HDM object that HDMOBJECT mirrors. Since a
% given HDM builds up data types and then objects from the fundamental types
% of 'int', 'float', 'complex', 'enum', and 'flag', the fields of the hdmObj
% can thus also be integers, real floats, complex floats, and logicals,
% though details of this can vary, depending upon how the mirroring is
% implemented outside of HDMOBJECT. HDMOBJECT was originally built to support
% ld_sbrplushdm().
%
% Since HDM objects define field names and associate them with types defined
% in the HDM, hdmObj will have corresponding field names and data types.
% Since an HDM object is, itself, a defined data type that can encapsulate
% other HDM objects, hdmObj can have fields whose values are other HDMOBJECTs.
% This is one reason why HdmObject is a sub-class of the MATLAB handle class.
% It allows an HDMOBJECT instance or sub-objects that it contains to be
% efficiently passed by reference without potentially expensive copying.
%
% COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.

properties
  hdmObj  % struct with unspecified fields
end  % properties
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
methods
  function obj = HdmObject(struct0)
    % constructor
    %
    % Example:
    %   myobject.myfield1 = 'a';
    %   myobject.myfield2 = [0 1 2];
    %   myHdmObject = HdmObject(myobject);
    %
    %   myHdmObject behaves as a MATLAB handle. One would access the fields
    %   as myHdmObject.hdmObj.<field_name> (e.g., myHdmObject.hdmObj.myfield1).
    %
    % Input Params:
    %  struct0 (struct) structure contents placed with public hdmObj property,
    %                   DEFAULT = []
    %
    % Returns:
    %  obj (object) HdmObject handle object whose hdmObj property matches
    %               the value passed in struct0
    if nargin > 0
      obj.hdmObj = struct0;
    end
  end  % constructor
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  function show(obj)
    % display contents of this object to console
    obj.hdmObj
  end
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

end  % methods
end  % class def