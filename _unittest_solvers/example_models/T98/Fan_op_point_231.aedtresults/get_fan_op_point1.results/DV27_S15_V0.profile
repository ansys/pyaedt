$begin 'Profile'
	$begin 'ProfileGroup'
		MajorVer=2023
		MinorVer=1
		Name='Solution Process'
		$begin 'StartInfo'
			I(1, 'Start Time', '06/20/2023 10:43:51')
			I(1, 'Host', 'AAPITTEGTDHIMV2')
			I(1, 'Processor', '16')
			I(1, 'OS', 'NT 10.0')
			I(1, 'Product', 'Icepak 2023.1.0')
		$end 'StartInfo'
		$begin 'TotalInfo'
			I(1, 'Elapsed Time', '00:00:05')
			I(1, 'ComEngine Memory', '71.4 M')
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
		ProfileItem('Design Validation', 0, 0, 0, 0, 0, 'I(3, 1, \'Level\', \'Perform full validations\', 1, \'Elapsed Time\', \'00:00:00\', 2, \'Memory\', 60080, true)', false, true)
		$begin 'ProfileGroup'
			MajorVer=2023
			MinorVer=1
			Name='Meshing Process'
			$begin 'StartInfo'
				I(1, 'Time', '06/20/2023 10:43:52')
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(1, 'Elapsed Time', '00:00:00')
			$end 'TotalInfo'
			GroupOptions=4
			TaskDataOptions('CPU Time'=8, Memory=8, 'Real Time'=8)
			ProfileItem('Global', 0, 0, 0, 0, 18088, 'I(4, 2, \'Nodes\', 10522, false, 2, \'Faces\', 2607, false, 2, \'Cells\', 8941, false, 0, \'Override min. gap - (1.600e-06, 1.600e-06, 5.000e-07)\')', true, true)
			ProfileFootnote('I(3, 2, \'Total Nodes\', 10522, false, 2, \'Total Faces\', 2607, false, 2, \'Total Cells\', 8941, false)', 0)
		$end 'ProfileGroup'
		ProfileItem('Populate Solver Input', 0, 0, 0, 0, 72712, 'I(1, 0, \'\')', true, true)
		ProfileFootnote('I(2, 1, \'Stop Time\', \'06/20/2023 10:43:57\', 1, \'Status\', \'Aborted\')', 1)
	$end 'ProfileGroup'
	$begin 'ProfileGroup'
		MajorVer=2023
		MinorVer=1
		Name='Solution Process'
		$begin 'StartInfo'
			I(1, 'Start Time', '06/20/2023 10:44:12')
			I(1, 'Host', 'AAPITTEGTDHIMV2')
			I(1, 'Processor', '16')
			I(1, 'OS', 'NT 10.0')
			I(1, 'Product', 'Icepak 2023.1.0')
		$end 'StartInfo'
		$begin 'TotalInfo'
			I(1, 'Elapsed Time', '00:00:20')
			I(1, 'ComEngine Memory', '67.8 M')
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
		ProfileItem('Design Validation', 0, 0, 0, 0, 0, 'I(3, 1, \'Level\', \'Perform full validations\', 1, \'Elapsed Time\', \'00:00:00\', 2, \'Memory\', 57544, true)', false, true)
		ProfileItem('Populate Solver Input', 0, 0, 0, 0, 69012, 'I(1, 0, \'\')', true, true)
		ProfileItem('Solver Initialization', 6, 0, 6, 0, 1045911, 'I(0)', true, true)
		$begin 'ProfileGroup'
			MajorVer=2023
			MinorVer=1
			Name='Transient Solution'
			$begin 'StartInfo'
				I(3, 'Initial Time', 0, '%f (s)')
			$end 'StartInfo'
			$begin 'TotalInfo'
				I(0, ' ')
			$end 'TotalInfo'
			GroupOptions=0
			TaskDataOptions(Memory=8)
			ProfileItem('Time - 1s', 0, 0, 0, 0, 0, 'I(1, 0, \'\')', false, true)
			ProfileItem('Time - 2s', 0, 0, 0, 0, 0, 'I(1, 0, \'\')', false, true)
			ProfileItem('Solve', 1, 0, 1, 0, 1098288, 'I(0)', true, true)
		$end 'ProfileGroup'
		ProfileFootnote('I(2, 1, \'Stop Time\', \'06/20/2023 10:44:32\', 1, \'Status\', \'Normal Completion\')', 0)
	$end 'ProfileGroup'
$end 'Profile'
