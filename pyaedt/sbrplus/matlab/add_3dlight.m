function hs = add_3dlight(hs,azel,mtrl,do_back)
% ADD_3DLIGHT add front and back lighting for 3-D rendering
%
% Input Params:
%  hs      (hndl) existing plot handle (pass through, not used directly)
%  azel (1x2 dbl) az and el angle for view [deg], DEFAULT = [30 30]
%  mtrl (1x4 dbl) reflectance properties [ka kd ks n],
%                 [ambient diffuse specular specular-exponent],
%                 DEFAULT = [0.3 1 0 1]
%
%  do_back  (lgc) true = add back light, false = don't (DEFAULT)
%
% Returns:
%  hs (struct)
%   (fields from input hs plus ...)
%   .light1 - first light (front light, used with update_lights.m function)
%   .light2 - second light (back light, used with update_lights.m function)
%
% hs = ADD_3DLIGHT(hs[,azel][,mtrl][,do_back])
%
% COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.

if (nargin < 2)
  azel = [30 30];
end
if (nargin < 3)
  mtrl = [0.3 1 0 1];
end
if (nargin < 4)
  do_back = false;
end

view(azel(1),azel(2));
axis equal;
axis vis3d;

hs.light1 = camlight('headlight');
set(hs.light1,'Style','infinite');
%
% Experimenting with not having a back light but, instead, using
% 'BackFaceLighting' = 'reverselit' for the surface lighting property.
%
if (do_back)
  hs.light2 = camlight('headlight');
  set(hs.light2,'Style','infinite');
  set(hs.light2,'Position',-get(hs.light2,'Position'));
end

material(mtrl);
end
