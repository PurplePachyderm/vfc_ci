module vfc_probes_f
    use, intrinsic :: iso_c_binding

    ! Structures

    type, bind(C) :: vfc_probe_node
        type(C_PTR) :: key
        real(kind=C_DOUBLE) :: val
    end type vfc_probe_node


    type, bind(C) :: vfc_hashmap_t
        integer(kind=C_SIZE_T) :: nbits
        integer(kind=C_SIZE_T) :: mask

        integer(kind=C_SIZE_T) :: capacity
        type(C_PTR) :: items
        integer(kind=C_SIZE_T) :: nitems
        integer(kind=C_SIZE_T) :: n_deleted_items
    end type vfc_hashmap_t


    type, bind(C) :: vfc_probes
        type(C_PTR) :: map
    end type vfc_probes


    ! Functions

    interface

        type(vfc_probes) function vfc_init_probes() bind(C, name = "vfc_init_probes")

        end function vfc_init_probes

        function vfc_free_probes(probes) bind(C, name = "vfc_free_probes")
            use, intrinsic :: iso_c_binding
            import :: vfc_probes

            type(vfc_probes) :: probes
        end function vfc_free_probes

        integer(C_INT) function vfc_probe(probes, testName, varName, val) bind(C, name = "vfc_probe")
            use, intrinsic :: iso_c_binding
            use ISO_C_BINDING
            import :: vfc_probes

            type(vfc_probes) :: probes
            type(C_PTR) :: testName
            type(C_PTR) :: varName
            real(kind=C_DOUBLE) :: val
        end function vfc_probe

        integer(C_INT) function vfc_remove_probe(probes, testName, varName) bind(C, name = "vfc_remove_probe")
            use, intrinsic :: iso_c_binding
            import :: vfc_probes

            type(vfc_probes) :: probes
            type(C_PTR) :: testName
            type(C_PTR) :: varName
        end function vfc_remove_probe

        integer(C_SIZE_T) function vfc_num_probes(probes) bind(C, name = "vfc_num_probes")
            use, intrinsic :: iso_c_binding
            import :: vfc_probes

            type(vfc_probes) :: probes
        end function vfc_num_probes

        integer(C_INT) function vfc_dump_probes(probes) bind(C, name = "vfc_dump_probes")
            use, intrinsic :: iso_c_binding
            import :: vfc_probes

            type(vfc_probes) :: probes
        end function vfc_dump_probes

    end interface

end module vfc_probes_f


! program vfc_probes_test
!     use iso_c_binding
! 	use vfc_probes_f
!     implicit none
!
!     type(vfc_probes), pointer :: probes
! 	integer(C_INT) :: err
!     real(kind=C_FLOAT) val
!     CHARACTER(len=10) :: test_name = 'test'//C_NULL_CHAR
!     CHARACTER(len=10) :: var_name = 'var'//C_NULL_CHAR
!
!     print *, "Testing Fortran interface"
!
!     val = 0.0
!
!     allocate(probes)
!     probes = vfc_init_probes()
!     ! err = vfc_probe(probes, test_name, var_name, val)
!     err = vfc_dump_probes(probes)
!
! end program vfc_probes_test
