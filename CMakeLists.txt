# Many of this is based on the scripts in the Polycode project.  Many thanks
# to the respective authors for going through the work of figuring this out!

cmake_minimum_required(VERSION 2.8.3)

# Set defaults.  Must be before project().
if(APPLE)
  set(CMAKE_OSX_ARCHITECTURES "x86_64" CACHE STRING "")
  set(CMAKE_OSX_DEPLOYMENT_TARGET "10.9" CACHE STRING "")
  set(CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LIBRARY "libc++")
endif()

project(panda3d-thirdparty)

include(ExternalProject)

set(DEFAULT_ENABLE ON)
if(DISABLE_ALL)
  set(DEFAULT_ENABLE OFF)
endif()

if(APPLE)
  set(NOT_APPLE OFF)
else()
  set(NOT_APPLE ${DEFAULT_ENABLE})
endif()

option(BUILD_ZLIB "Build zlib" ${DEFAULT_ENABLE})
option(BUILD_PNG "Build zlib (requires zlib)" ${DEFAULT_ENABLE})
option(BUILD_ASSIMP "Build assimp (requires zlib)" ${NOT_APPLE})
option(BUILD_BULLET "Build bullet" ${DEFAULT_ENABLE})
option(BUILD_HARFBUZZ "Build harfbuzz (requires freetype)" ${DEFAULT_ENABLE})
option(BUILD_FREETYPE "Build freetype (requires harfbuzz, zlib and png)" ${DEFAULT_ENABLE})
option(BUILD_VORBIS "Build vorbis" ${DEFAULT_ENABLE})
option(BUILD_OPUS "Build opus" ${DEFAULT_ENABLE})
option(BUILD_OPENAL "Build OpenAL" ${NOT_APPLE})
option(BUILD_JPEG "Build libjpeg" ${DEFAULT_ENABLE})
option(BUILD_SQUISH "Build libsquish" ${DEFAULT_ENABLE})
option(BUILD_FCOLLADA "Build FCollada" ${DEFAULT_ENABLE})
option(BUILD_VRPN "Build VRPN" ${DEFAULT_ENABLE})
option(BUILD_TIFF "Build TIFF (requires zlib and jpeg)" ${DEFAULT_ENABLE})
option(BUILD_EIGEN "Copy Eigen headers" ${DEFAULT_ENABLE})
option(BUILD_ODE "Build ODE physics engine" ${DEFAULT_ENABLE})
option(BUILD_ARTOOLKIT "Build ARToolKit" ${DEFAULT_ENABLE})
option(BUILD_NVIDIACG "Copy NVIDIA Cg Toolkit binaries" ${DEFAULT_ENABLE})
option(BUILD_OPENSSL "Build OpenSSL" ${DEFAULT_ENABLE})
option(BUILD_OPENEXR "Build OpenEXR" ${DEFAULT_ENABLE})
option(BUILD_FFMPEG "Build FFMpeg (requires vorbis, freetype and zlib)" ${DEFAULT_ENABLE})
option(BUILD_GLSLANG "Build glslang" ${DEFAULT_ENABLE})
option(BUILD_SPIRV_CROSS "Build spirv-cross" ${DEFAULT_ENABLE})
option(BUILD_SPIRV_TOOLS "Build spirv-tools" ${DEFAULT_ENABLE})


if(CMAKE_GENERATOR MATCHES "^Visual Studio [0-9]+ ")
  string(REPLACE " " ";" WORDS ${CMAKE_GENERATOR})
  list(GET WORDS 2 VCVER)
  set(THIRDPARTY_DIR ${CMAKE_SOURCE_DIR}/win-libs-vc${VCVER})

  if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(THIRDPARTY_DIR "${THIRDPARTY_DIR}-x64")
  endif()

elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
  set(THIRDPARTY_DIR ${CMAKE_SOURCE_DIR}/darwin-libs-a)

elseif(CMAKE_SYSTEM_NAME STREQUAL "Linux")
  if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(THIRDPARTY_DIR ${CMAKE_SOURCE_DIR}/linux-libs-x64)
  else()
    set(THIRDPARTY_DIR ${CMAKE_SOURCE_DIR}/linux-libs-a)
  endif()

elseif(CMAKE_SYSTEM_NAME STREQUAL "FreeBSD")
  if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    set(THIRDPARTY_DIR ${CMAKE_SOURCE_DIR}/freebsd-libs-x64)
  else()
    set(THIRDPARTY_DIR ${CMAKE_SOURCE_DIR}/freebsd-libs-a)
  endif()

else()
  message(FATAL_ERROR "Unknown platform.")
endif()

if(NOT MSVC)
  set(CMAKE_C_FLAGS "-fpic")
  set(CMAKE_CXX_FLAGS "-fpic")
endif()

message("thirdparty packages will be installed to ${THIRDPARTY_DIR}")

set(COMMON_CMAKE_ARGS
  -DCMAKE_C_FLAGS=${CMAKE_C_FLAGS}
  -DCMAKE_CXX_FLAGS=${CMAKE_CXX_FLAGS}
  -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR>
  -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
  -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
  -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
  -DCMAKE_LINKER=${CMAKE_LINKER}
  -DCMAKE_TOOLCHAIN_FILE=${CMAKE_TOOLCHAIN_FILE}
  -DCMAKE_INSTALL_LIBDIR=lib
  -DBUILD_SHARED_LIBS=OFF
  -DSKIP_INSTALL_EXECUTABLES=ON
  -DSKIP_INSTALL_FILES=ON
)

if(APPLE)
  # Prevent the semicolon from becoming a space in the command.
  string(REPLACE ";" "$<SEMICOLON>" archs "${CMAKE_OSX_ARCHITECTURES}")
  set(COMMON_CMAKE_ARGS ${COMMON_CMAKE_ARGS}
    -DCMAKE_OSX_ARCHITECTURES=${archs}
    -DCMAKE_OSX_DEPLOYMENT_TARGET=${CMAKE_OSX_DEPLOYMENT_TARGET}
    -DCMAKE_OSX_SYSROOT=${CMAKE_OSX_SYSROOT}
  )
endif(APPLE)

if(BUILD_ZLIB)
  ExternalProject_Add(
    zlib
    GIT_REPOSITORY https://github.com/madler/zlib.git

    CMAKE_ARGS ${COMMON_CMAKE_ARGS}
      -DZLIB_TESTS=OFF
    INSTALL_DIR ${THIRDPARTY_DIR}/zlib
  )

  # Remove the shared libraries, which cannot be disabled in the CMake file.
  if(WIN32)
    ExternalProject_Add_Step(zlib remove_extras
      COMMAND ${CMAKE_COMMAND} -E remove_directory "<INSTALL_DIR>/bin"
      COMMAND ${CMAKE_COMMAND} -E remove_directory "<INSTALL_DIR>/share"
      COMMAND ${CMAKE_COMMAND} -E remove "<INSTALL_DIR>/lib/zlib.lib"
      DEPENDEES install
    )
  elseif(APPLE)
    ExternalProject_Add_Step(zlib remove_extras
      COMMAND ${CMAKE_COMMAND} -E remove "<INSTALL_DIR>/lib/libz.dylib"
                                         "<INSTALL_DIR>/lib/libz.1.dylib"
                                         "<INSTALL_DIR>/lib/libz.1.2.11.dylib"
      DEPENDEES install
    )
  else()
    ExternalProject_Add_Step(zlib remove_extras
      COMMAND ${CMAKE_COMMAND} -E remove "<INSTALL_DIR>/lib/libz.so"
                                         "<INSTALL_DIR>/lib/libz.so.1"
                                         "<INSTALL_DIR>/lib/libz.so.1.2.11"
      DEPENDEES install
    )
  endif()
endif()

if(BUILD_PNG)
  ExternalProject_Add(
    png
    DEPENDS zlib

    # Please note that libpng 1.6.32+ requires CMake 3.0.2
    GIT_REPOSITORY https://github.com/glennrp/libpng.git

    CMAKE_ARGS ${COMMON_CMAKE_ARGS}
      -DCMAKE_PREFIX_PATH=${THIRDPARTY_DIR}/zlib
      -DPNG_SHARED=OFF
      -DPNG_STATIC=ON
      -DPNG_TESTS=OFF
      -DPNG_DEBUG=OFF
      -DAWK= # Needed for multi-arch build on macOS
    INSTALL_DIR ${THIRDPARTY_DIR}/png
  )

  ExternalProject_Add_Step(png remove_extras
    COMMAND ${CMAKE_COMMAND} -E remove_directory "<INSTALL_DIR>/lib/libpng"
    DEPENDEES install
  )
endif()

if(BUILD_HARFBUZZ)
  # Ugh, freetype and harfbuzz depend on each other?!  Madness.  Well, we'll
  # have to make a temporary build of freetype so we can build HarfBuzz.
  ExternalProject_Add(
    freetype-nohb
    DEPENDS zlib png
    URL https://download.savannah.gnu.org/releases/freetype/freetype-2.10.2.tar.xz

    CMAKE_ARGS ${COMMON_CMAKE_ARGS}
      -DCMAKE_PREFIX_PATH=${THIRDPARTY_DIR}/zlib;${THIRDPARTY_DIR}/png
      -DWITH_HarfBuzz=OFF
      -DWITH_BZip2=OFF
      -DPNG_INCLUDE_DIRS=${THIRDPARTY_DIR}/png/include
    INSTALL_DIR ${CMAKE_CURRENT_BINARY_DIR}/freetype-nohb
  )

  # Use the tarball instead of git repo in order to avoid the need for ragel.
  ExternalProject_Add(
    harfbuzz
    DEPENDS freetype-nohb
    URL https://www.freedesktop.org/software/harfbuzz/release/harfbuzz-2.6.7.tar.xz

    CMAKE_ARGS ${COMMON_CMAKE_ARGS}
      -DCMAKE_PREFIX_PATH=${CMAKE_CURRENT_BINARY_DIR}/freetype-nohb
      -DHB_HAVE_FREETYPE=ON
      -DHB_BUILD_TESTS=OFF
      -DHB_BUILD_UTILS=OFF
      -DHB_BUILD_SUBSET=OFF
      -DHB_HAVE_INTROSPECTION=OFF
      -DHB_HAVE_CORETEXT=OFF # macOS 10.8+
      -DFREETYPE_INCLUDE_DIR_freetype2=${CMAKE_CURRENT_BINARY_DIR}/freetype-nohb/include/freetype2
      -DFREETYPE_INCLUDE_DIR_ft2build=${CMAKE_CURRENT_BINARY_DIR}/freetype-nohb/include/freetype2
    INSTALL_DIR ${THIRDPARTY_DIR}/harfbuzz
  )

  ExternalProject_Add_Step(harfbuzz move_headers
    COMMAND ${CMAKE_COMMAND} -E rename "<INSTALL_DIR>/include/harfbuzz" "<INSTALL_DIR>/include-tmp"
    COMMAND ${CMAKE_COMMAND} -E remove_directory "<INSTALL_DIR>/include"
    COMMAND ${CMAKE_COMMAND} -E rename "<INSTALL_DIR>/include-tmp" "<INSTALL_DIR>/include"
    COMMAND ${CMAKE_COMMAND} -E remove_directory "<INSTALL_DIR>/lib/cmake"
    DEPENDEES install
  )
endif()

if(BUILD_FREETYPE)
  ExternalProject_Add(
    freetype
    DEPENDS zlib png harfbuzz
    URL https://download.savannah.gnu.org/releases/freetype/freetype-2.10.2.tar.xz

    CMAKE_ARGS ${COMMON_CMAKE_ARGS}
      -DCMAKE_PREFIX_PATH=${THIRDPARTY_DIR}/zlib;${THIRDPARTY_DIR}/png;${THIRDPARTY_DIR}/harfbuzz
      -DWITH_HarfBuzz=ON
      -DWITH_BZip2=OFF
      -DPNG_INCLUDE_DIRS=${THIRDPARTY_DIR}/png/include
      -DHARFBUZZ_INCLUDE_DIRS=${THIRDPARTY_DIR}/harfbuzz/include
      -DPC_HARFBUZZ_INCLUDEDIR=${THIRDPARTY_DIR}/harfbuzz/include
      -DPC_HARFBUZZ_LIBDIR=${THIRDPARTY_DIR}/harfbuzz/lib
    INSTALL_DIR ${THIRDPARTY_DIR}/freetype
  )

  ExternalProject_Add_Step(freetype remove_extras
    COMMAND ${CMAKE_COMMAND} -E remove_directory "<INSTALL_DIR>/lib/cmake"
    DEPENDEES install
  )
endif()