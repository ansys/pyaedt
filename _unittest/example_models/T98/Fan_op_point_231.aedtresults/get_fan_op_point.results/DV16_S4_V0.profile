$begin 'Profile'
	$begin 'ProfileGroup'
		MajorVer=2023
		MinorVer=1
		Name='Solution Process'
		$begin 'StartInfo'
			I(1, 'Start Time', '06/20/2023 10:45:05')
			I(1, 'Host', 'AAPITTEGTDHIMV2')
			I(1, 'Processor', '16')
			I(1, 'OS', 'NT 10.0')
			I(1, 'Product', 'Icepak 2023.1.0')
		$end 'StartInfo'
		$begin 'TotalInfo'
			I(1, 'Elapsed Time', '00:00:16')
			I(1, 'ComEngine Memory', '71.7 M')
		$end 'TotalInfo'
		GroupOptions=8
		TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
		ProfileItem('', 0, 0, 0, 0, 0, 'I(1, 1, \'Executing From\', \'C:\\\\Program Files\\\\AnsysEM\\\\v231\\\\Win64\\\\ICEPAKCOMENGINE.exe\')', false, true)
		$begin 'ProfileGroup'
			MajorVer=2023
			MinorVer=1
			Name='HPC'
			$begin 'StartInfo'
				I(1, 'Type', 'Manual')
				I(1, 'Distribution Types', 'Variations, Solver, Mesher')
				I(1, 'MPI Vendor', 'Intel')
				I(1, 'MPI Version', '2018')
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(0, ' ')
			$end 'TotalInfo'
			GroupOptions=0
			TaskDataOptions(Memory=8)
			ProfileItem('Machine', 0, 0, 0, 0, 0, 'I(3, 1, \'Name\', \'AAPitTegtDhimv2.win.ansys.com\', 2, \'Tasks\', 1, false, 2, \'Cores\', 4, false)', false, true)
		$end 'ProfileGroup'
		ProfileItem('Design Validation', 0, 0, 0, 0, 0, 'I(3, 1, \'Level\', \'Perform full validations\', 1, \'Elapsed Time\', \'00:00:00\', 2, \'Memory\', 60528, true)', false, true)
		$begin 'ProfileGroup'
			MajorVer=2023
			MinorVer=1
			Name='Meshing Process'
			$begin 'StartInfo'
				I(1, 'Time', '06/20/2023 10:45:05')
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(1, 'Elapsed Time', '00:00:00')
			$end 'TotalInfo'
			GroupOptions=4
			TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
			ProfileItem('Global', 0, 0, 0, 0, 18088, 'I(4, 2, \'Nodes\', 10522, false, 2, \'Faces\', 2607, false, 2, \'Cells\', 8941, false, 0, \'Override min. gap - (1.600e-06, 1.600e-06, 5.000e-07)\')', true, true)
			ProfileFootnote('I(3, 2, \'Total Nodes\', 10522, false, 2, \'Total Faces\', 2607, false, 2, \'Total Cells\', 8941, false)', 0)
		$end 'ProfileGroup'
		ProfileItem('Populate Solver Input', 0, 0, 0, 0, 73136, 'I(1, 0, \'\')', true, true)
		ProfileItem('Solver Initialization', 6, 0, 6, 0, 1300926, 'I(0)', true, true)
		ProfileItem('Solve', 1, 0, 0, 0, 1366231, 'I(0)', true, true)
		ProfileFootnote('I(2, 1, \'Stop Time\', \'06/20/2023 10:45:21\', 1, \'Status\', \'Normal Completion\')', 0)
	$end 'ProfileGroup'
$end 'Profile'
