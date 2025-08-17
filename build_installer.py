  File "C:\Users\elidr\Desktop\Stitcher\optimized_stitcher_git\build_installer.py", line 296, in <module>
    success = main()
              ^^^^^^
  File "C:\Users\elidr\Desktop\Stitcher\optimized_stitcher_git\build_installer.py", line 275, in main
    if not build_executable():
           ^^^^^^^^^^^^^^^^^^
    # Find all DLLs in the virtual environment
    all_dlls = find_all_dlls(python_dir)
    print(f"Found {len(all_dlls)} DLL files to include")
    
    # Find all DLLs in the virtual environment
    all_dlls = find_all_dlls(python_dir)
    print(f"Found {len(all_dlls)} DLL files to include")
    
  File "C:\Users\elidr\Desktop\Stitcher\optimized_stitcher_git\build_installer.py", line 108, in build_executable
    spec_content = create_spec_file(python_dir, pyqt6_path, all_dlls)
                                                            ^^^^^^^^
NameError: name 'all_dlls' is not defined