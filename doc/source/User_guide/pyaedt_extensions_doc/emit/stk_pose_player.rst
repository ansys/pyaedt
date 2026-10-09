STK pose player
===============

The **STK pose player** extension replays the position and orientation timeline logged by the
EMIT-STK plugin into the EMIT scene, so that object alignment can be verified in the
**Couplings** dialog 3D view.

When an STK scenario runs, the EMIT-STK plugin writes a summary log next to the file named by
the ``ANSYS_STK_UI_PLUGIN_LOG`` environment variable. For example, a log path of
``C:\temp\stk_ui_plugin.log`` produces ``C:\temp\stk_ui_plugin_summary.csv``. That CSV holds one
row per receiver and timestep, describing the pose of the moving platform relative to the
stationary ground platform.

The extension provides a Graphical User Interface (GUI) for configuration.


Features
--------

- Parse the ``*_summary.csv`` written by the EMIT-STK plugin.
- Step forward and backward through timesteps, or play through them automatically with a
  configurable delay.
- Normalize X, Y, and Z independently using each axis's maximum absolute coordinate across
  all objects and timesteps in the loaded log. Signs are preserved and zero-only axes remain zero. A true-range mode is
  also available for comparison.
- Display positions and orientations for every object at every timestep, alongside the
  true range and logged EMI margin. The active timestep's rows are highlighted and scrolled
  into view during stepping and playback.
- Restore the original positions and orientations when finished.


Using the extension
-------------------

1. Open the **Couplings** dialog in EMIT and select a node under **Scene** so the 3D view is
   showing. The 3D view updates live while it is visible, and it cannot be selected
   programmatically.
2. Open the **Automation** tab in the EMIT interface.
3. Locate and click the **STK Pose Player** icon under the Extension Manager.
4. Browse to the ``*_summary.csv`` written by the EMIT-STK plugin and click **Load**.
5. Use **Prev**, **Next**, **Play**, **Pause**, and **Stop**, or drag the slider, to move
   through the timeline.
6. Adjust **Target range (m)** and click **Apply** to change the normalization, or clear
   **Normalize range** to place objects at their true separation.
7. Click **Restore original** when finished, or answer the prompt shown when closing the
   extension.


Notes
-----

- The summary log is sampled on at least a 60 second cadence, so playback is coarse relative
  to the STK animation step.
- Independent axis normalization changes relative directions and Euclidean distances;
  **Target range (m)** is an axis limit, not an object separation distance.
- Poses are applied to the EMIT scene group whose name matches the ``Group Node`` column.
  Objects with no matching scene group are reported in the status line.
- HFSS-linked antennas and nodes that use a phase center cannot be repositioned from EMIT.
