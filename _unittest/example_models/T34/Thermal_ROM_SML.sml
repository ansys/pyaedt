SMLDEF Thermal_ROM_SML
{

     PORT real in : Input1_InternalHeatGeneration;
     PORT real in : Input2_HeatFlow;

     PORT real in : Ref1_Temp1 = 2.951500e+02;
     PORT real in : Ref2_Temp2 = 2.951500e+02;

     PORT real out : Output1_Temp1 = sssm.OutVec[0];
     PORT real out : Output2_Temp2 = sssm.OutVec[1];

     INTERN NCStateSpaceModel sssm
     (
        NumOutputs := 2,  NumInputs := 4,  
        InVec[0] := Input1_InternalHeatGeneration , 
        InVec[1] := Input2_HeatFlow , 
        InVec[2] := Ref1_Temp1 , 
        InVec[3] := Ref2_Temp2 , 
        NumStates := 16 ,  
        Mode := 3 ,  
        A_row :=
        0
        1
        3
        5
        6
        7
        9
        11
        12
        13
        14
        15
        16
        18
        20
        21
        ,
        A_col :=
        0
        1
        2
        1
        2
        3
        4
        5
        6
        5
        6
        7
        8
        9
        10
        11
        12
        13
        12
        13
        14
        15
        ,
        A_NonZeros := 22
        ,
        MatrixA :=
        -1.088280e-01
        0.000000e+00
        1.000000e+00
        -6.578639e-03
        -6.795586e-03
        -4.334062e-03
        -1.719193e+00
        0.000000e+00
        1.000000e+00
        -8.089552e-04
        -3.902651e-03
        -4.524139e-03
        -1.185993e+00
        -9.632427e-02
        -4.795756e-03
        -4.318334e-03
        0.000000e+00
        1.000000e+00
        -3.008413e-03
        -1.904252e-03
        -4.033259e-03
        -2.004892e-02
        , 
        B_row :=
        0
        1
        1
        2
        3
        4
        4
        5
        6
        7
        8
        9
        10
        10
        11
        12
        ,
        B_col :=
        0
        0
        0
        1
        1
        1
        0
        0
        0
        0
        1
        1
        1
        ,
        B_NonZeros := 13
        ,
        MatrixB :=
        1.569859e-08
        1.569859e-08
        1.569859e-08
        5.000000e-01
        5.000000e-01
        5.000000e-01
        1.569859e-08
        1.569859e-08
        1.569859e-08
        1.569859e-08
        5.000000e-01
        5.000000e-01
        5.000000e-01
        , 
        C_row :=
        0
        8
        ,
        C_col :=
        0
        1
        2
        3
        4
        5
        6
        7
        8
        9
        10
        11
        12
        13
        14
        15
        ,
        C_NonZeros := 16
        ,
        MatrixC :=
        1.577107e-02
        -6.230525e-06
        -1.732583e-05
        5.174927e-03
        1.763584e+00
        2.605549e-06
        5.971550e-05
        1.493263e-03
        9.628570e-01
        1.471336e-02
        2.037277e-04
        5.018707e-03
        2.093970e-06
        1.080787e-04
        1.238091e-03
        9.353277e-04
        , 
        D_row :=
        0
        1
        ,
        D_col :=
        2
        3
        ,
        D_NonZeros := 2
        ,
        MatrixD :=
        1.000000e+00
        1.000000e+00
     );
}
