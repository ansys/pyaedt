function obj = ld_wfobj(fname)
% LD_WFOBJ load Wavefront OBJ file
%
% This reader is targeted toward OBJ files exported from HFSS through the
% Model -> Export ... menu. While intended to be a general purpose OBJ file
% reader, it is not tested outside of this context.
%
% Parses a subset of OBJ format files, recognizing the following keys:
%   mtllib <mtl_file_name>
%   usemtl <mtrl_name>
%   v <x> <y> <z>       3D vertex points
%   vn <nx> <ny> <nz>   3D normals, not necessarily unit normals
%   vt <u> <v> <w>      3D texture coords <v> and <w> default to 0 if missing
%   f <v1> <v2> <v3>    triangle face vertex connectivity, <vi> are integer
%                       indices starting from 1 that cross-ref the ordered
%                       list of vertex 'v' lines in the vertex block
%                       immediately preceding the face list, negative indices
%                       cross-ref the vertex block in backward order, starting
%                       from -1 as the last vertex in the preceding block
%
%   More generally, will parse triangle faces that specify indices to
%   the preceding block text coords and vertex normals, using forward slash
%   '/' as a delimiter
%   f <v1>/<vt1>/<vn1> <v2>/<vt2>/<vn2> <v3>/<vt3>/<vn3>
%   f <v1>/<vt1> <v2>/<vt2> <v3>/vt3>
%   f <v1>//<vn1> <v2>//<vn2> <v3>//<vn3>
%
% Input Params:
%  fname (str) full path name of .hdm file, DEFAULT = [] = select
%              interactively from file dialog
%
% Returns:
%  obj (struct)
%   .mfile  {Nm x 1 cell} cell array of material file names
%   .mtllib {Nm x 1 cell} cell array of loaded material file data, one
%                         cell element per material file whose content
%            (1xM struct) is an array of structs, one array element per
%                         material read from the file (1..M)
%
%   .mname  {Nm}{Nn} nested cell array of material names used, in order
%                    mtllib and usemtl keys are encountered in OBJ file
%
%   .midx   {Nm}{Nn} mapping from mtllib file index (1..Nm) and usemtl named
%                    material (1..Nn) to struct array index for matching
%                    material in mtllib, index = 0 if no match
%
%   .vrt    (Nv x 3 dbl) concatenated list of vertices
%   .vtxt   (Nv x 3 dbl) concatenated list of texture coords
%   .vnrm   (Nv x 3 dbl) concatenated list of vertex normals
%   .fv     (Nf x 3 int) concatenated list of triangle vertex indices
%   .ft     (Nf x 3 int) concatenated list of triangle texture indices
%   .fn     (Nf x 3 int) concatenated list of triangle vert normal indices
%   .fm     (Nf x 1 int) face mtrl index, use to access second cell dimension
%                        {Nn} of .mname and .midx
%
%   .fmfile (Nf x 1 int) face material file index, use to access first cell
%                        dimension {Nm} of .mname and .midx
%
% obj = LD_WFOBJ([fname])
%
% COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.

if ~exist('fname','var') fname = ''; end

if isempty(fname)
  % file name not provided, obtain interactively from file dialog
  [fname pathname] = uigetfile('*.obj','Open Wavefront OBJ geometry file');
  if fname
    fname = fullfile(pathname,fname);
  else
    error('ld_wfobj:noFileSpecified','No file specified to load');
  end
end

[dirpath,froot,ext] = fileparts(fname);

obj = [];
fid = fopen(fname);
if fid == -1
  error('ld_wfobj:fileError','Could not open %s',fname);
end

Nmtl_file = 0;  % number of mtllib file names
mfile = [];     % cell array of mtllib file names
Nmtl = 0;       % number of usemtl material names for current file
mname = [];     % nested cell array of usemtl material names, {imfile}{jmname}

% OBJ file is assumed to be organized in blocks where face vertex indices
% are encoded local to the block. A new block starts when, while reading
% lists of faces, the next line is for something other than a face, such
% as a vertex line or new material spec line.
vrt_blk = [];   % 3D vertices block
vtxt_blk = [];  % texture vertices block
vnrm_blk = [];  % vertex normals block
fv_blk = [];    % face vertex indices block
ft_blk = [];    % face texture vertex indices block
fn_blk = [];    % face vertex normal indices block

vrt = [];  % composite 3D vertices
vtxt = []; % composite texture vertices
vnrm = []; % composite vertex normals
fv = [];   % composite face vertex indices
ft = [];   % composite face texture vertex indices
fn = [];   % composite face vertex normals indices
fm = [];   % composite face material indices
fmfile = [];  % composite face material file indices

  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  function next_part_block()
  % call this whenever reading anything other than a face lines
  if reading_faces
    % Reading the first line of a new block.
    %
    % Augment the composite list of vertices and face indices with
    % block-local quantities, making necessary adjustment from block-local
    % vertex indices to composite vertex indices.
    %
    % While we expect the number of texture vertices in a block to either be
    % zero (0) or equal to the number of 3D point vertices, the code logic
    % does not assume or require this. Thus, we have different offsets for
    % each vertex type to go from block-local to composite.
    %
    % Convert negative vertex indices into equivalent positive ones.
    % -1 means last block local vertex read, -2 means the one before that,
    % and so on. If the block has 3 vertices, then they can be referenced in
    % the following way:
    %   v1 <-- 1 or -3
    %   v2 <-- 2 or -2
    %   v3 <-- 3 or -1
    %
    idx = find(fv_blk < 1);
    fv_blk(idx) = fv_blk(idx) + size(vrt_blk,1) + 1;
    idx = find(ft_blk < 1);
    ft_blk(idx) = ft_blk(idx) + size(vtxt_blk,1) + 1;
    idx = find(fn_blk < 1);
    fn_blk(idx) = fn_blk(idx) + size(vnrm_blk,1) + 1;

    % append faces for part block to composite faces list,
    % converting block-local vertex indices to composite ones
    fv = [fv;fv_blk + size(vrt,1)];
    ft = [ft;ft_blk + size(vtxt,1)];
    fn = [fn;fn_blk + size(vnrm,1)];

    % append vertices for block to composite vertex lists
    vrt = [vrt;vrt_blk];
    vtxt = [vtxt;vtxt_blk];
    vnrm = [vnrm;vnrm_blk];

    vrt_blk = [];
    vtxt_blk = [];
    vnrm_blk = [];
    fv_blk = [];
    ft_blk = [];
    fn_blk = [];

    reading_faces = false;
  end
  end  % next_part_block
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

reading_faces = false;
line_count = 0;
while true
  [aline line_count] = next_line(fid,line_count);
  if isempty(aline)
    next_part_block();  % process final face lines
    break;  % EOF, stop reading
  end

  key = sscanf(aline,'%s',1);
  switch key
   case 'mtllib'
    next_part_block();
    mfile0 = sscanf(aline(8:end),'%s');
    Nmtl_file = Nmtl_file + 1;
    mfile{Nmtl_file} = mfile0;
    Nmtl = 0;  % this counter is local to material file

   case 'usemtl'
    next_part_block();
    mname0 = sscanf(aline(8:end),'%s');
    Nmtl = Nmtl + 1;
    mname{Nmtl_file}{Nmtl} = mname0;

   case 'v'
    next_part_block();
    v0 = sscanf(aline(3:end),'%f');
    vrt_blk = [vrt_blk;v0'];

   case 'vt'
    next_part_block();
    v0 = sscanf(aline(4:end),'%f');
    vtxt_blk = [vtxt_blk;v0'];

   case 'vn'
    next_part_block();
    v0 = sscanf(aline(4:end),'%f');
    vnrm_blk = [vnrm_blk;v0'];

   case 'f'
    reading_faces = true;
    faces0 = textscan(aline(3:end),'%d','Delimiter','/');
    faces0 = transpose(faces0{1});
    Nidx = length(faces0);
    fv0 = []; ft0 = []; fn0 = [];
    if Nidx == 3
      fv0 = faces0;
    elseif Nidx == 6
      fv0 = faces0(1:2:end);
      ft0 = faces0(2:2:end)'
    elseif Nidx == 9
      fv0 = faces0(1:3:end);
      fn0 = faces0(3:3:end);
      if faces0(2) ~= 0
        ft0 = faces0(2:3:end);
      end
    else
      fclose(fid);
      errMsg = sprintf(['Unrecognized face line format encountered on line ' ...
                        '%d of file:\n  %s\nbad line: %s'], ...
                        line_count,fname,aline);
      error('ld_wfobj:unexpectedFormatting',errMsg);
    end

    % cache vertex indices in block-local containers for now, this will be
    % reconciled in next_part_block() after reading the entire face block
    fv_blk = [fv_blk;fv0];
    ft_blk = [ft_blk;ft0];
    fn_blk = [fn_blk;fn0];

    % material info can go straight into the composite lists
    fm = [fm;Nmtl];
    fmfile = [fmfile;Nmtl_file];

  otherwise
    wrnMsg = sprintf(['Unrecognized OBJ entity key, %s, encountered on ' ...
                      'line %d of file:\n  %s\nMoving on.'], ...
                     key,line_count,fname);
    warning(wrnMsg);
  end
end
fclose(fid);

% Load any MTL files as named by mtllib keys
[dirpath0 froot0 ext0] = fileparts(fname);
for imtl_file = 1:Nmtl_file
  fname_mtl = mfile{imtl_file};
  [dirpath1 froot1 ext1] = fileparts(fname_mtl);
  if isempty(dirpath1)
    % MTL file named by mtllib line in OBJ file has no directory path, assume
    % it's in the same directory as the OBJ file
    fname_mtl = fullfile(dirpath0,[froot1 ext1]);
  end
  try
    mtllib0 = ld_wfmtl(fname_mtl);  % returns struct array
    mtllib{imtl_file} = mtllib0;
  catch me
    mtllib{imtl_file} = [];
    wrnMsg = sprintf(['Trouble while loading referenced MTL file:\n' ...
                      '  %s\n%s\nMoving on.'],fname_mtl,me.message());
    warning(wrnMsg);
  end
end

% build a map from the 2D cell container of usemtl material names (mname)
% to the index of the corresponding material data struct in mtllib. Like
% mname, this map will be a 2D cell array of the same size, so there is
% a one-to-one correspondence.
for imtl_file = 1:Nmtl_file
  map1 = containers.Map();
  Nmtl_in_lib = length(mtllib{imtl_file});
  for imtl = 1:Nmtl_in_lib
    % looping all materials found in current MTL file
    map1(mtllib{imtl_file}(imtl).name) = imtl;
  end
  for imtl = 1:Nmtl
    % Looping all materials named by usemtl keys for current MTL file
    mname0 = mname{imtl_file}{imtl};
    if map1.isKey(mname0);
      midx{imtl_file}{imtl} = map1(mname0);
    else
      midx{imtl_file}{imtl} = 0;
    end
  end
end

obj.mfile = mfile;
obj.mtllib = mtllib;
obj.mname = mname;
obj.midx = midx;
obj.vrt = vrt;
obj.vtxt = vtxt;
obj.vnrm = vnrm;
obj.fv = fv;
obj.ft = ft;
obj.fn = fn;
obj.fm = fm;
obj.fmfile = fmfile;

end  % ld_wfobj
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function mtllib = ld_wfmtl(fname)
% LD_WFMTL load a Wavefront OBJ material library file
%
% Supports of subset of the MTL format, recognizing the following keys:
%   newmtl <material_name>
%   Ka <r> <g> <b>  - RGB value of ambient lighting color
%   Kd <r> <g> <b>  - RGB value of diffuse shading color
%
% Input Params:
%  fname (str) full path name of .mtl file
%
% Returns:
%  mtllib (1 x Nm struct) list of material properties
%   .name        (str) material name
%   .amb_rgb (1x3 dbl) RGB value of ambient lighting color
%   .dfs_rgb (1x3 dbl) RGB value of diffuse lighting color

mtllib = [];
fid = fopen(fname);
if fid == -1
  error('ld_wfmtl:fileError','Could not open %s',fname);
end

mtl0.name = '';
mtl0.amb_rgb = [0 0 0];  % black
mtl0.dfs_rgb = [0.8 0.8 0.8];  % grey

Nmtl = 0;
%mname = {};
%amb_rgb = [];
%dfs_rgb = [];
line_count = 0;
while true
  [aline line_count] = next_line(fid,line_count);
  if isempty(aline)
    break;  % EOF, stop reading
  end

  key = sscanf(aline,'%s',1);
  switch lower(key)
   case 'newmtl'
    mname0 = sscanf(aline(8:end),'%s');
    Nmtl = Nmtl + 1;
    mtllib = [mtllib mtl0];
    mtllib(Nmtl).name = mname0;

   case 'ka'
    if Nmtl == 0
      wrnMsg = ...
        sprintf(['Encountered Ka key line before first encountering a ' ...
                 'newmtl key line to own it on line %d of file:\n  %s\n' ...
                 'Ignoring this key line and moving on.'],line_count,fname);
      warning(wrnMsg);
    end

    [rgb0 Nflt] = sscanf(aline(4:end),'%f');
    if Nflt ~= 3 || (size(rgb0,1) ~= 3)
      wrnMsg = ...
        sprintf(['Encountered Ka key line not followed by 3 float numbers ' ...
                 'for R,G,B values on line %d of file:\n  %s\nbad line: %s'], ...
                line_count,fname,aline);
      warning(wrnMsg);
    end
    mtllib(Nmtl).amb_rgb = transpose(rgb0);

   case 'kd'
    if Nmtl == 0
      wrnMsg = ...
        sprintf(['Encountered Kd key line before first encountering a ' ...
                 'newmtl key line to own it on line %d of file:\n  %s\n' ...
                 'Ignoring this key line and moving on.'],line_count,fname);
      warning(wrnMsg);
    end

    [rgb0 Nflt] = sscanf(aline(4:end),'%f');
    if Nflt ~= 3 || (size(rgb0,1) ~= 3)
      wrnMsg = ...
        sprintf(['Encountered Kd key line not followed by 3 float numbers ' ...
                 'for R,G,B values on line %d of file:\n  %s\nbad line: %s'], ...
                line_count,fname,aline);
      warning(wrnMsg);
    end
    mtllib(Nmtl).dfs_rgb = transpose(rgb0);

   otherwise
    wrnMsg = sprintf(['Unrecognized MTL entity key, %s, encountered on ' ...
                      'line %d of file:\n  %s\nMoving on.'], ...
                     key,line_count,fname);
    warning(wrnMsg);
  end
end
fclose(fid);


end  % ld_mtlfile

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [buff new_count] = next_line(fid,line_count)
% finds and returns next non-comment line in file
%
% Skips blank lines and line content after first '#'
%
% Input Params:
%   fid        (int) file ID from fopen function
%   line_count (int) total lines read so far, including comment lines
%
% Returns:
%   buff      (string) next non-comment line found, empty [] if EOF
%   new_count (int) line number of next non-comment line found
%
% [buff new_count] = next_line(fid,line_count)

new_count = line_count;
buff = fgets(fid);
while (buff ~= -1)
  new_count = new_count + 1;
  buff = strtrim(buff);  % remove leading and trailing white space
  if isempty(buff)
    % blank line, get next one
    buff = fgets(fid);
    continue;
  end

  idx = find(buff == '#',1);
  if isempty(idx)
    return;  % return with active line
  end

  % remove content after '#'
  if idx == 1
    % effectively a blank line, get the next one
    buff = fgets(fid);
    continue;
  end
  buff = buff(1:(idx - 1));
  return;  % return with active line
end

% encountered EOF
buff = [];

end  % next_line