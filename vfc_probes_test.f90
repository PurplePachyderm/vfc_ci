program vfc_probes_test
    use iso_c_binding
	use vfc_probes_f
    implicit none

    type(vfc_probes) :: probes
    integer(C_INT) :: err
    integer(C_SIZE_T) n_probes

    print *, "Testing Fortran interface"
    probes = vfc_init_probes()
    ! err = vfc_dump_probes(probes)

end program vfc_probes_test
