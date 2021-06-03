program vfc_probes_test
    use iso_c_binding
	use vfc_probes_f
    implicit none

    type(vfc_probes) :: probes
	type(C_PTR) :: a

    ! probes = vfc_init_probes

	a = test_interface()



end program vfc_probes_test
