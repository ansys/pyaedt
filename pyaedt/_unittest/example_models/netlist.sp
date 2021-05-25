* 0;Circuit1.sph
**************************************************************************************************
*                                            Circuit Design netlist                                      *
*                             created by ANSYS Electronics Desktop                            *
**************************************************************************************************

.option PARHIER='local'
.option max_messages=1
.option num_threads=4

* begin toplevel circuit

C1 0 net_1 1e-12
Q2 net_1 Port1 net_2
R3 net_2 0 50
L4 0 Port1 L=1e-09
RPort1 Port1 0 PORTNUM=1 RZ=50 IZ=0
.PORT Port1 0 1 RPort1

* end toplevel circuit
.end