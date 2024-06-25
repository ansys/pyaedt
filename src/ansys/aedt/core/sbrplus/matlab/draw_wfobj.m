function hs = draw_wfobj(obj,alpha,face_clr,edge_clr,skip_mtl,do_light)
% DRAW_WFOBJ draw Wavefront OBJ model imported using ld_wfobj()
%
% Input Params:
%  obj (struct) Wavefront OBJ struct returned by ld_wfobj()
%
%  alpha        (dbl) alpha-channel opacity, 1.0 = totally opaque (DEFAULT)
%  face_clr (1x3 dbl) face color {[R G B], MATLAB color string, 'none', 'flat'}
%            OR (str) MATLAB color string can be a preset color, its short
%                     name, or a hex RGB color string (e.g., 'red', 'g',
%                     '#ff0088'), set to 'flat' (DEFAULT) to color according
%                     to diffuse color data as found in MTL file referenced in
%                     the OBJ file (see ld_wfobj() )
%
%  edge_clr (1x3 dbl) edge color {[R G B], MATLAB color string, 'none'}
%            or (str) see doc for face_clr, set to 'none' (DEFAULT) to switch
%                     off rendering of edges
%
%  skip_mtl     (str) set to value of 'usemtl' key line in OBJ file to switch
%                     off rendering of all faces to which it applies,
%                     DEFAULT = '' = don't skip rendering any faces
%
%  do_light     (lgc) true = add 3D lighting (DEFAULT)
%
% Returns:
%   hs (struct) handles for displayed object
%    .surf (1xN hndl) plot handle for surface patches, this will be a
%                     vector of handles when face_clr == 'flat', one handle
%                     for each group of faces of a given diffuse material color
%
%    .light1   (hndl) front light (used by update_lights() )
%    .light2   (hndl) back light (used by update_lights() )
%
% hs = DRAW_WFOBJ(obj[,alpha][,face_clr][,edge_clr][,skip_mtl][,do_light])
%
% COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.

if ~exist('alpha','var') alpha = []; end
if isempty(alpha) alpha = 1.0; end

if ~exist('face_clr','var') face_clr = []; end
if isempty(face_clr) face_clr = 'flat'; end

if ~exist('edge_clr','var') edge_clr = []; end
if isempty(edge_clr) edge_clr = 'none'; end

if ~exist('skip_mtl','var') skip_mtl = []; end

if ~exist('do_light','var') do_light = []; end
if isempty(do_light) do_light = true; end

if ~isempty(skip_mtl)
  ikeep = ones(size(obj.fv,1),1,'logical');
  Nmtl_file = length(obj.mfile);
  for imtl_file = 1:Nmtl_file
    Nmtl = length(obj.mname{imtl_file});
    for imtl = 1:Nmtl
      if strcmp(skip_mtl,obj.mname{imtl_file}{imtl})
        ikeep = ikeep & (obj.fmfile ~= imtl_file | obj.fm ~= imtl);
      end
    end
  end
  idx = find(ikeep);
  obj.fv = obj.fv(idx,:);
  if ~isempty(obj.ft)
    obj.ft = obj.ft(idx,:);
  end
  if ~isempty(obj.fn)
    obj.fn = obj.fn(idx,:);
  end
  obj.fm = obj.fm(idx,:);
  obj.fmfile = obj.fmfile(idx,:);
end


if strcmp(face_clr,'flat')
  % render obj faces according to their assigned diffuse color from
  % ld_wfobj()
  Nsurf = 0;
  Nmtl_file = length(obj.mfile);
  for imtl_file = 1:Nmtl_file
    Nmtl = length(obj.mname{imtl_file});
    for imtl = 1:Nmtl
      idx = find((obj.fmfile == imtl_file) & (obj.fm == imtl));
      if ~isempty(idx)
        mtl_clr = '#a0a0a0';
        idx_mtl = obj.midx{imtl_file}{imtl};
        if idx_mtl
          mtl_clr = obj.mtllib{imtl_file}(idx_mtl).dfs_rgb;
        end
        hs0 = trisurf(obj.fv(idx,:),obj.vrt(:,1),obj.vrt(:,2),obj.vrt(:,3));
        hold on;
        set(hs0,'BackFaceLighting','lit');
        %set(hs0,'BackFaceLighting','reverselit');
        set(hs0,'FaceAlpha',alpha);
        set(hs0,'EdgeColor',edge_clr);
        set(hs0,'FaceColor',mtl_clr);
        Nsurf = Nsurf + 1;
        hs.surf(Nsurf) = hs0;
      end
    end
  end
  hold off;

else
  % render obj faces with specified color, face_clr
  hs0 = trisurf(obj.fv,obj.vrt(:,1),obj.vrt(:,2),obj.vrt(:,3));
  set(hs0,'BackFaceLighting','lit');
  %set(hs0,'BackFaceLighting','reverselit');
  set(hs0,'FaceAlpha',alpha);
  set(hs0,'EdgeColor',edge_clr);
  set(hs0,'FaceColor',face_clr);
  hs.surf = hs0;
end

if do_light
  az_deg = 30;
  el_deg = 30;
  ka = 0.3;   % ambient reflectance
  kd = 1.0;   % diffuse reflectance
  ks = 0;     % specular reflectance
  do_backlight = true;
  mtrl_refl = [ka kd ks];
  hs = add_3dlight(hs,[az_deg el_deg],mtrl_refl,do_backlight);
end

end  % draw_obj
