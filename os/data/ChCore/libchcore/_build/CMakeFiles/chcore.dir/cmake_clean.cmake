file(REMOVE_RECURSE
  "libchcore.a"
  "libchcore.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang C)
  include(CMakeFiles/chcore.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
