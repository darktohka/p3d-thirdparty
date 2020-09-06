@echo off

set ARCH=x86
if not "%1"=="" set ARCH=%1

if %ARCH%==x86 (
  set CMAKE_ARCH=Win32
) else (
  set CMAKE_ARCH=x64
)

rmdir build /s /q
rmdir win-libs-vc14 /s /q
rmdir win-libs-vc14-x64 /s /q
mkdir build
cd build

call "C:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" %ARCH%
cmake -DCMAKE_BUILD_TYPE=Release -A %CMAKE_ARCH% ..
cmake --build . --target ALL_BUILD --config Release
cd ..
tar -czvf libs.tar.gz win-libs-*