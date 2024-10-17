classdef SbrBounceType < int8
% SBRBOUNCETYPE enumeration class for signifying different types of SBR
% ray bounces
%
% This enumeration is introduced by filter_rays1 so that ray tracks imported
% from SBR+ HDM files can have their source points and, if applicable, UTD
% edge diffraction points encoded as ray-bounce HdmObjects that parent the
% first_bounce HdmObject from the HDM import. Doing this simplifies ray track
% post-processing logic for recursively traversing ray track trees by
% representing all points along the ray track in a consistent way.
%
% COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.
enumeration
  Undefined (0)
  Source    (1)
  UtdEdge   (2)
  Surface   (3)
end
end  % SbrBounceType class def