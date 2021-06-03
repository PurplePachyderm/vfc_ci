module vfc_probes_f
    use, intrinsic :: iso_c_binding

    ! Structures

    type, bind(C) :: vfc_probe_node
        type(C_PTR) :: key
        real(kind=C_DOUBLE) :: val
    end type vfc_probe_node


    type, bind(C) :: vfc_hashmap_t
        integer(C_SIZE_T) :: nbits
        integer(C_SIZE_T) :: mask

        integer(C_SIZE_T) :: capacity
        type(C_PTR) :: items
        integer(C_SIZE_T) :: nitems
        integer(C_SIZE_T) :: n_deleted_items
    end type vfc_hashmap_t


    type, bind(C) :: vfc_probes
        type(C_PTR) :: map
    end type vfc_probes


    ! Functions

    interface

		type(C_PTR) function test_interface() bind(C, name = "test_interface")

		end function test_interface

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
