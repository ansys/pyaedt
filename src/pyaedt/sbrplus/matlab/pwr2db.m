function db = pwr2db(pwr)
% PWR2DB convert linear-scale relative power to decibels (dB)
%
% Input Params:
%  pwr  (MxN dbl) relative power on linear scale
%
% Returns:
%  db   (MxN dbl) 10 log10(pwr)
%
% db = PWR2DB(pwr)
%
% COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.
db = 10*log10(pwr);
end  % pwr2db

