classdef StopWatch < handle
 % STOPWATCH stop watch for timing processes
 %
 % Can be started, stopped, and started again to time processes spread out
 % over separate blocks of code.
 %
 % Versions:
 %   1 5-feb-2019 Initial version
 %
 % COPYRIGHT ANSYS, Inc. ALL RIGHTS RESERVED.
 properties (SetAccess = protected)
  mTimeMark
  mIsRunning
  mTimeElapsed
 end  % StopWatch properties
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 methods
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  function obj = StopWatch()
  % StopWatch constructor
  %
  % Returns reset StopWatch: not running, zero elapsed time, ready to start
  %
  % obj = StopWatch()
  obj.reset();
  end  % StopWatch constructor
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  function start(obj)
  % start or restart the stopwatch
  %
  % Does nothing if stopwatch is already running (except harm accuracy
  % slightly through its overhead).
  %
  % start()
  if ~obj.mIsRunning
    obj.mTimeMark = tic;
    obj.mIsRunning = true;
  end
  end  % start

  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  function stop(obj)
  % stop the stopwatch
  %
  % Does nothing if stopwatch is already stopped.
  % Stopwatch can later be restarted (via start())
  %
  % stop()
  if obj.mIsRunning
    obj.mTimeElapsed = obj.mTimeElapsed + toc(obj.mTimeMark);
    obj.mTimeMark = 0;
    obj.mIsRunning = false;
  end
  end  % stop

  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  function reset(obj)
  % reset the stopwatch
  %
  % Stops stopwatch and resets its elapsed time. All timing information
  % is lost, but StopWatch object can now be used as a fresh timer.
  %
  % reset()
  obj.mTimeMark = 0;
  obj.mIsRunning = false;
  obj.mTimeElapsed = 0;
  end  % reset

  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  function elap_tm = elapsedTime(obj)
  % returns the elapsed time on the stop watch [s]
  %
  % For best accuracy, stop the stopwatch before consulting and reporting
  % elapsed time, as any live activity inevitably adds overhead that is
  % captured in the reported elapsed time.
  %
  % elap_tm = elapsedTime()
  if obj.mIsRunning
    % obj.mTimeElapsed not updated until stopwatch is stopped,
    % so need to tack on elapsed time since stopwatch was last started.
    elap_tm = obj.mTimeElapsed + toc(obj.mTimeMark);
  else
    elap_tm = obj.mTimeElapsed;
  end
  end  % elapsedTime
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 end  % StopWatch methods
end  % StopWatch class def
