module vfc_probes_struct
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
        type(vfc_hashmap_t) :: map
    end type vfc_probes

end module vfc_probes_struct


module vfc_probes
    ! Functions

    use, intrinsic :: iso_c_binding
    use vfc_probes_struct

    interface

        function vfc_init_probes() bind(C, name = "vfc_init_probes") result(probes)
            type(vfc_probes) :: probes
        end function vfc_init_probes

        function vfc_free_probes(probes) bind(C, name = "vfc_free_probes")
            type(vfc_probes) :: probes
        end function vfc_free_probes

        function vfc_probe(probes, testName, varName, val) bind(C, name = "vfc_probe") result(error)
            type(vfc_probes) :: probes
            type(C_PTR) :: testName
            type(C_PTR) :: varName
            real(kind=C_DOUBLE) :: val

            type(C_INT) :: error
        end function vfc_probe

        function vfc_remove_probe(probes, testName, varName) bind(C, name = "vfc_remove_probe") result(error)
            type(vfc_probes) :: probes
            type(C_PTR) :: testName
            type(C_PTR) :: varName

            int(C_INT) :: error
        end function vfc_remove_probe

        function vfc_num_probes(probes) bind(C, name = "vfc_num_probes") result(nProbes)
            type(vfc_probes) :: probes

            int(C_SIZE_T) :: nProbes
        end function vfc_num_probes

        function vfc_dump_probes(probes) bind(C, name = "vfc_dump_probes") result(error)
            type(vfc_probes) :: probes

            integer(C_INT) :: error
        end function vfc_dump_probes

    end interface
end module vfc_probes


program vfc_probes
    print *, 'Hello, World!'
end program vfc_probes
