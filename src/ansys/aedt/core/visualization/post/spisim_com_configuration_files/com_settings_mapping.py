# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

spimsim_matlab_keywords_mapping = {
    # Matlab keyword -> SPIsim keyword
    # OP_IO_CTRL
    "BESSEL_THOMSON": "BESSEL_THOMSON",  # enable Bessel Thomsen filter for COM
    "Butterworth": "BUTTERWORTH",  # enable Butterworth filter for TDR, PTDR, and ERL
    "CDR": "CDR",  # CDR method, default is 'MM' (Mueller-Muller)
    "COM Pass threshold": "COM_PASS_THRESHOLD",  # the pass fail threshold for COM in dB
    "Enforce Causality DIFF_TOL": "EC_DIFF_TOL",
    # Difference Tolerance parameter for causality, Hard enforcement, 1e-4,Soft enforcement, 1e-3
    "Enforce Causality pulse start tolerance": "EC_PULSE_TOL",
    # Tolerance parameter for causality, Hard enforcement, 0.05, Soft enforcement, .01
    "Enforce Causality REL_TOL": "EC_REL_TOL",
    # Difference Tolerance parameter for causality, Hard enforcement, 1e-4,Soft enforcement, 1e-3
    "EH_MAX": "EH_MAX",  # used when PMD_type is C2M and is not really computed per spec
    "EH_MIN": "EH_MIN",  # used when PMD_type is C2M
    "ENFORCE_CAUSALITY": "ENFORCE_CAUSALITY",  # default is 0. Not recommended to use
    "ERL Pass threshold": "ERL_PASS_THRESHOLD",  # the pass fail threshold for ERL in dB
    "Error propagation COM margin": "ERR_PROPAGATION_COM_MARGIN",
    # Use to calculate  error propagation (not normally used)
    "Force PDF bin size": "FORCE_PDF_BIN_SIZE",  # do not use
    "Histogram_Window_Weight": "HISTOGRAM_WINDOW_WEIGHT",
    # Weighting for VEC and VEO are histogram processing. Type are Gaussian,Dual Rayleigh,Triangle, and Rectangle
    # (default)
    "Impulse response truncation threshold": "IMPRSP_TRUNC_THRESHOLD",  # Impulse response truncation threshold
    "Include PCB": "INCLUDE_PCB",  # Used to add a PCB one each side of the passed s-parameters.
    "nburst": "MAX_BURST_LEN",  # Use to calculate burst error rate (not normally used)
    "Min_VEO_Test": "MIN_VEO_TEST",
    # used when PMD_type is C2M. This allow EH to go blow EH_min. If set to Zero it is ignored
    "N_v": "N_V",  # number of UI used to compute Vf
    "Optimize_loop_speed_up": "OPTIMIZE_LOOP_SPEED_UP",
    # If set to 0 (or default) normal looping, If set to 1 loop speedup by slightly reducing PD Fbin and FIR_threshold
    # for optimize looping only
    "Port Order": "PORT_ORDER",  # s parameter port order [ tx+ tx- rx+ rx-]
    "RUNTAG": "RUNTAG",  # This string is appended to the beginning of results files
    "SBR_GEN_METHOD": "SBR_GEN_METHOD",  # Pulse generation method: use IBIS's slew rate or filtered rectangular pause
    "sigma_r": "SIGMA_R",  # sigma_r for 0.3ck Gaussian histogram window. Unit are UI. Preferred usage.
    "TDECQ": "TDECQ",  # Experimental, for only option is none (0) or vma. Default is 0.
    "TDR_W_TXPKG": "TDR_W_TXPKG",  # adds tx package for TDR, PTDR, and ERL. Default is 0.
    "USE_ETA0_PSD": "USE_ETA0_PSD",  # Used eta_0 PSD equation for sigma_n. Default is 0. Do not use.
    "VEC Pass threshold": "VEC_PASS_THRESHOLD",  # the pass fail threshold for VEC in dB only used when PMD_type is C2M
    # TABLE_93A1
    "A_fe": "A_FE",  # FEXT aggressor differential peak source output voltage (half of peak to peak)
    "A_ne": "A_NE",  # NEXT aggressor differential peak source output voltage (half of peak to peak)
    "A_v": "A_V",  # Victim differential peak source output voltage (half of peak to peak)
    "AC_CM_RMS": "AC_CM_RMS",
    # AC_CM_RMS is the CM BBN AWGN RMS at COM source point. Default is 0. Adds common mode noise source to the COM
    # signal path for the through channel
    "ACCM_MAX_Freq": "ACCM_MAX_FREQ",  # F max for integrating ACCM voltage in Hz. Default is fb
    "C_b": "C_B",  # C_b in nF (single sided)
    "C_d": "C_D",  # C_d in nF (single sided)
    "C_p": "C_P",  # C_p in nF (single sided)
    "C_V": "C_V",  # C_v in nF (via cap)  (single sided)
    "Delta_f": "DELTA_F",  # frequency step
    "DER_0": "DER_0",  # Target detector error ratio
    "f_b": "F_B",  # Baud (Signaling) rate in Gbaud
    "f_min": "F_MIN",  # minimum required frequency start for s parameters
    "f_v": "F_V",  # For FOM_ILD: Transition rate cutoff frequency for ICN/ILD calc in terms of fb
    "L": "L",  # number of symbols levels (PAM-4 is 4, NRZ is 2)
    "L_s": "L_S",  # L_s in nH (single sided)
    "Local Search": "LOCAL_SEARCH",  # Decreases COM compute time. Setting to 2 seems ok ,if 0 search is full grid
    "M": "M",  # Samples per UI
    "N_B_STEP": "N_B_STEP",  # Discretization of DFE, 0 disables and is not normally used
    "N_bx": "N_BX",  # Used for ERL to Compensate for a number of Ui associated with the DFE
    "R_0": "R_0",  # reference impedance
    "R_d": "R_D",  # Die source termination resistance  (single sided)
    "samples_for_C2M": "SAMPLES_FOR_C2M",  # Finer sampling in terms of samples per UI for c2m histogram analysis.
    "T_h": "T_O",  # superseded with T_O but is the internal values that is used. Do not use.
    "z_p (FEXT)": "Z_PFEXT",  # List of FEXT transmitter package trace lengths in mm, one per case
    "z_p (NEXT)": "Z_PNEXT",  # List of NEXT transmitter package trace lengths in mm, one per case
    "z_p (RX)": "Z_PRX",  # List of FEXT receiver package trace lengths in mm, one per case
    "z_p select": "Z_PSELECT",  # List of package length indexes used to run COM
    "z_p (TX)": "Z_PTX",  # List of victim transmitter package trace lengths in mm, one per case
    # TABLE_93A3
    "package_tl_gamma0_a1_a2": "PACKAGE_TL_GAMMA0_A1_A2",
    # Fitting parameters for package model per unit length. First element is in 1/mm and affects DC loss of package
    # model . Second element is in ns1/2/mm and affects loss proportional to sqrt(f). Third element is in ns/mm and
    # affects loss proportional to f.
    "package_tl_tau": "PACKAGE_TL_TAU",  # Package model transmission line delay ns/mm
    "package_Z_c": "PACKAGE_Z_C",  # Package model transmission line characteristic impedance [ Tx , Rx ]
    # TABLE_9212
    "board_tl_gamma0_a1_a2": "BOARD_TL_GAMMA0_A1_A2",
    # Fitting parameters for package model per unit length. First element is in 1/mm and affects DC loss of package
    # model . Second element is in ns1/2/mm and affects loss proportional to sqrt(f). Third element is in ns/mm and
    # affects loss proportional to f.
    "board_tl_tau": "BOARD_TL_TAU",  # Board model transmission line delay ns/mm
    "board_Z_c": "BOARD_Z_C",  # Board model transmission line characteristic impedance [ Tx , Rx ]
    "C_0": "CB0",  # If Include PCB is set to 1, near device single ended capacitance C0  in nF is added
    "C_1": "CB1",  # if Include PCB is set to 1, connector side single ended capacitance C1 in nF is added
    "z_bp (FEXT)": "Z_BPFEXT",  # Fext Assessor transmitter board trace lengths in mm
    "z_bp (NEXT)": "Z_BPNEXT",  # Next Assessor transmitter board trace lengths in mm
    "z_bp (RX)": "Z_BPRX",  # Victim receiver board trace lengths in mm
    "z_bp (TX)": "Z_BPTX",  # Victim transmitter board trace lengths in mm
    # TDR_ERL
    "AUTO_TFX": "AUTO_TFX",  # Mostly used for device ERL. If sent to 1 the fixture tfx will be estimated.
    "beta_x": "BETA_X",  # (for ERL) use default 0
    "BTorder": "BT_ORDER",  # Bessel function order
    "ERL": "ERL",  # Enables ERL. Needs TDR to be set as well.
    "ERL_ONLY": "ERL_ONLY",  # Compute ERL only
    "FIXTURE_BUILTIN_DELAY": "FIXTURE_BUILTIN_DELAY",  # built-in fixture delay
    "fixture delay time": "FIXTURE_DELAY_TIME",  # fixture delay time (for ERL)
    "N": "N",  # duration time in UI which is used for ERL (PTDR)
    "rho_x": "RHO_X",  # (for ERL) use default 0.618
    "TDR_DURATION": "TDR_DURATION",
    # only used if N*UI is longer than the TDR duration time.  Default is 5 times the raw s-parameter transit time.
    "TR_TDR": "TR_TDR",  # Gaussian shaped transition time for TDR source in ns
    "Turkey_Window": "TUKEY_WINDOW",  # required for ERL. Set to 1. Default is 0.
    "Z_T": "Z_T",  # single sided source termination reference resistance for TDR and ERL
    # ICN_PARAM
    "A_ft": "A_FT",  # FEXT aggressor amplitude for ICN. Defaults to A_fe if not specified
    "A_nt": "A_NT",  # NEXT aggressor amplitude for ICN. Defaults to A_ne if not specified
    "f_1": "F_1",  # start frequency for ICN and ILD calculations in GHz
    "f_2": "F_2",  # frequency in GHz for integration computation of ICN or FOM_Ild in GHz
    "f_f": "F_F",  # For ICN: Fext transition rate cut off frequency for ICN calc in terms of fb
    "f_n": "F_N",  # For ICN: Next transition rate cut off frequency for ICN calc in terms of fb
    # FILTER_EQ
    "__b_max(1)": "B_MAX1",  # DFE magnitude limit, first coefficient(ignored if Nb=0)
    "__b_max(2..N_b)": "B_MAX2_N_B",
    # DFE magnitude limit, second coefficient and on (ignored if Nb<2). Can be a regular expression
    "b_min(1)": "B_MIN1",  # DFE negative magnitude limit. If not specified it defaults to -bmax.
    "b_min(2..N_b)": "B_MIN2_N_B",  # DFE negative magnitude limit, if not specified it defaults to -__b_max(2..N_b)
    "c(-1)": "C_1",  # TX equalizer pre cursor tap -1
    "c(-2)": "C_2",  # TX equalizer pre cursor tap -2
    "c(-3)": "C_3",  # TX equalizer pre cursor tap -3
    "c(-4)": "C_4",  # TX equalizer pre cursor tap -4
    "c(0)": "C0",
    # TX equalizer cursor minimum value (actual value is calculated as 1-sum(abs(tap)), Grid seat ignored for when C(0)
    # is below this value
    "c(1)": "C1",  # TX equalizer post cursor tap 1
    "c(2)": "C2",  # TX equalizer post cursor tap 2
    "c(3)": "C3",  # TX equalizer post cursor tap 3
    "CTLE_TYPE": "CTLE_TYPE",  # Sets the CTLE type default is poles and zeros (i.e. not a list of poles as in 120e)
    "F_HP_P": "F_HP_P",  # CFT pole fp2 is in GHz. Normally a list for 120e. Not normally use elsewhere.
    "f_HP_PZ": "F_HP_PZ",  # CFT pole zero pair in GHz for low frequency CTF
    "F_HP_Z": "F_HP_Z",  # CFT pole zero pair in GHz for low frequency CTF
    "f_p1": "F_P1",  # CTLE pole 1 in GHz
    "f_p2": "F_P2",  # CTLE pole 2 in GHz
    "f_r": "F_R",  # Receiver filter in COM and in ICN/FOM_ILD calcs in terms of fb
    "f_z": "F_Z",  # CTLE zero in GHz
    "g_DC": "G_DC",  # AC-DC gain list
    "g_DC_HP": "G_DC_HP",  # CTF AC-DC gain list (GDC2)
    "G_Qual": "G_QUAL",  # G_Qual are the dB ranges of g_DC g DC )which correspond tog_DC_HP (g DC2)
    "G2_Qual": "G2_QUAL",
    # G2_Qual limit values of g_DC_HP (g DC2 ) which corresponds to ranges of g_DC g DC specified with G_QUAL
    "GDC_MIN": "GDC_MIN",  # max ACDC gain, if 0 ignore
    "N_b": "N_B",  # Decision feedback fixed equalizer (DFE) length
    # NOISE_JITTER
    "A_DD": "A_DD",  # Normalized peak dual-Dirac noise, this is half of the total bound uncorrelated jitter (BUJ) in UI
    "eta_0": "ETA_0",
    # One-sided noise spectral density (V^2/GHz).Input referred noise at TP5. Input referred noise at TP5
    "R_LM": "R_LM",  # Ratio of level separation mismatch. Relevant when not PAM-2 (NRZ).
    "sigma_RJ": "SIGMA_RJ",  # rms of random jitter
    "SNR_TX": "SNR_TX",  # Transmitter SNDR noise in dB
    # RCV_NONSTD
    "FORCE_TR": "FORCE_TR",  # Included for earlier version support but should be set to 1 in most later config sheets.
    "Grr": "GRR",  # either do no use or set to 1 (for ERL)
    "GRR_LIMIT": "GRR_LIMIT",  # either do no use or set to 1 (for ERL)
    "Gx": "GX",  # ERL parameter param.Grr, This is used is the COM code
    "IDEAL_RX_TERM": "IDEAL_RX_TERM",
    # IDEAL_RX_TERM not supported, instead, set Zp,Cd, and Cp parameters to zero and Zp select to 1
    "IDEAL_TX_TERM": "IDEAL_TX_TERM",  # not supported, instead, set Zp,Cd, and Cp parameters to zero and Zp select to 1
    "INC_PACKAGE": "INC_PACKAGE",
    # warning: INC_PACKAGE=0 not fully supported, instead, set Zp,Cd, and Cp parameters to zero and Zp select to 1
    "INCLUDE_CTLE": "INCLUDE_CTLE",  # do not use
    "INCLUDE_TX_RX_FILTER": "INCLUDE_TX_RX_FILTER",  # do not use
    "kappa1": "KAPPA1",  # if set 0 reflection at tp0 are omitted from COM
    "kappa2": "KAPPA2",  # if set 0 reflection at tp5 are omitted from COM
    "RX_CALIBRATION": "RX_CALIBRATION",  # Turn on RX_Calibration loop
    "Sigma BBN step": "SIGMA_BBN_STEP",  # BBN step for Rx Calibration in volts. Defaults is 0.5e-3
    "T_r": "T_R",  # 20% to 80% transition time used for the Gaussian shaped source
    "T_R_FILTER_TYPE": "T_R_FILTER_TYPE",  # included for earlier version support. Not recommended to use.
    "T_R_MEAS_POINT": "T_R_MEAS_POINT",  # included for earlier version support. Not recommended to use.
    # FLOATING_TAPS
    "B_float_RSS_MAX": "B_FLOAT_RSS_MAX",  # floating DFE tap start for RSS floating tap limit
    "bmaxg": "BMAXG",  # max DFE value for floating taps
    "N_bf": "N_BF",  # number of taps in group
    "N_bg": "N_BG",  # number of group of floating tap. Used as a switch, 0 means no float
    "N_f": "N_F",  # UI span for floating taps. replaced by N_bmax
    "N_tail_start": "N_TAIL_START",  # start range for max RSS limit for DFE taps
    # RX_FFE
    "CURSOR_GAIN": "CURSOR_GAIN",  # only FFE and not supported
    "FFE_BACKOFF": "FFE_BACKOFF",
    # see if better zero forced solution is better by backing off the number specified FFE taps one at at time
    "FFE_MAIN_CUR_MIN": "FFE_MAIN_CUR_MIN",  # Rx FFE main cursor minimum
    "ffe_post_tap_len": "FFE_POST_TAP_LEN",  # Rx FFE post cursor tap length
    "FFE_POST_TAP1_MAX": "FFE_POST_TAP1_MAX",  # Rx FFE post cursor tap1 limit
    "ffe_pre_tap_len": "FFE_PRE_TAP_LEN",  # Rx FFE pre-cursor tap length
    "FFE_PRE_TAP1_MAX": "FFE_PRE_TAP1_MAX",  # Rx FFE pre cursor tap1 limit
    "FFE_TAP_STEP_SIZE": "FFE_TAP_STEP_SIZE",  # Rx FFE tap step size
    "FFE_TAPN_MAX": "FFE_TAPN_MAX",  # Rx FFE precursor tap N limit
    "Tukey_Window": "TUKEY_WINDOW",
    "TDR": "TDR",
    "NEXTARY": "NEXTARY",
    "HISTOGRAM_WINDOW_WEIGHT": "HISTOGRAM_WINDOW_WEIGHT",
    "OPTIMIZE_LOOP_SPEED_UP": "OPTIMIZE_LOOP_SPEED_UP",
    "EC_PULSE_TOL": "EC_PULSE_TOL",
    "VEC_PASS_THRESHOLD": "VEC_PASS_THRESHOLD",
    "KAPPA1": "KAPPA1",
    "VERSION": "VERSION",
    "PDF_BIN_SIZE": "PDF_BIN_SIZE",
    "RESULT_DIR": "RESULT_DIR",
    "G_QUAL": "G_QUAL",
    "T_O": "T_O",
    "TDR_BUTTERWORTH": "TDR_BUTTERWORTH",
    "GRR": "GRR",
    "SPECTAG": "SPECTAG",
    "FFE_PRE_TAP_LEN": "FFE_PRE_TAP_LEN",
    "FEXTARY": "FEXTARY",
    "GENHTML": "GENHTML",
    "SIGMA_R": "SIGMA_R",
    "FFE_POST_TAP_LEN": "FFE_POST_TAP_LEN",
    "MIN_VEO_TEST": "MIN_VEO_TEST",
    "ACCM_MAX_FREQ": "ACCM_MAX_FREQ",
    "N_V": "N_V",
    "BUTTERWORTH": "BUTTERWORTH",
    "IMPRSP_TRUNC_THRESHOLD": "IMPRSP_TRUNC_THRESHOLD",
    "EC_DIFF_TOL": "EC_DIFF_TOL",
    "C_4": "C_4",
    "ERR_PROPAGATION_COM_MARGIN": "ERR_PROPAGATION_COM_MARGIN",
    "EC_REL_TOL": "EC_REL_TOL",
    "MAX_BURST_LEN": "MAX_BURST_LEN",
    "FSTTHRU": "FSTTHRU",
    "BT_ORDER": "BT_ORDER",
    "PMD_TYPE": "PMD_TYPE",
    "C3": "C3",
    "C2": "C2",
    "F_1": "F_1",
    "G2_QUAL": "G2_QUAL",
    "NUMPORT": "NUMPORT",
    "NOISE_CREST_FACTOR": "NOISE_CREST_FACTOR",
    "THRUSNP": "THRUSNP",
    "SAMPLES_FOR_C2M": "SAMPLES_FOR_C2M",
    "GX": "GX",
}
