"""
C/C++ project detection - Make, CMake, Bazel, Meson
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import re
from .base import LanguageDetector


class CppDetector(LanguageDetector):
    """Detect C/C++ projects and their configuration"""

    def detect(self) -> bool:
        """Check if this is a C/C++ project"""
        markers = [
            'Makefile',
            'makefile',
            'GNUmakefile',
            'CMakeLists.txt',
            'BUILD',  # Bazel
            'BUILD.bazel',
            'WORKSPACE',  # Bazel
            'meson.build',  # Meson
            'configure.ac',  # Autotools
            'configure.in',
            '*.c',
            '*.cpp',
            '*.cc',
            '*.cxx',
            '*.h',
            '*.hpp',
            '*.hxx'
        ]

        for marker in markers:
            if self.find_files(marker):
                return True
        return False

    def analyze(self) -> Dict[str, Any]:
        """Analyze C/C++ project configuration"""
        config = {
            'language': 'c++',
            'variant': self._detect_variant(),
            'build_system': self._detect_build_system(),
            'compiler': self._detect_compiler(),
            'standard': self._detect_standard(),
            'testing': self._detect_testing(),
            'dependencies': self._detect_dependencies(),
            'project_type': self._detect_project_type(),
        }

        return config

    def _detect_variant(self) -> str:
        """Detect if C or C++"""
        # Count file types
        c_files = len(self.find_files('**/*.c'))
        cpp_files = (len(self.find_files('**/*.cpp')) +
                     len(self.find_files('**/*.cc')) +
                     len(self.find_files('**/*.cxx')))

        if cpp_files > c_files:
            return 'c++'
        elif c_files > 0:
            return 'c'

        # Check build files for hints
        if self._check_cmake_language():
            return self._check_cmake_language()

        return 'c++'  # Default to C++

    def _detect_build_system(self) -> Dict[str, Any]:
        """Detect which build system is used"""
        build = {
            'system': None,
            'config_file': None,
            'build_command': None,
            'clean_command': None,
            'test_command': None,
        }

        # CMake (most common for C++)
        if (self.project_root / 'CMakeLists.txt').exists():
            build['system'] = 'cmake'
            build['config_file'] = 'CMakeLists.txt'

            # Check for presets
            if (self.project_root / 'CMakePresets.json').exists():
                build['has_presets'] = True
                build['configure_command'] = 'cmake --preset default'
                build['build_command'] = 'cmake --build --preset default'
            else:
                build['configure_command'] = 'cmake -B build'
                build['build_command'] = 'cmake --build build'

            build['clean_command'] = 'rm -rf build'
            build['test_command'] = 'ctest --test-dir build'

            # Check for build directory
            if (self.project_root / 'build').exists():
                build['build_dir'] = 'build'
            elif (self.project_root / 'cmake-build-debug').exists():
                build['build_dir'] = 'cmake-build-debug'  # CLion default

        # Make
        elif self._find_makefile():
            makefile = self._find_makefile()
            build['system'] = 'make'
            build['config_file'] = makefile.name
            build['build_command'] = 'make'
            build['clean_command'] = 'make clean'

            # Parse Makefile for common targets
            targets = self._parse_makefile_targets(makefile)
            if 'test' in targets:
                build['test_command'] = 'make test'
            elif 'check' in targets:
                build['test_command'] = 'make check'

            if 'install' in targets:
                build['install_command'] = 'make install'

        # Bazel
        elif (self.project_root / 'WORKSPACE').exists() or (self.project_root / 'WORKSPACE.bazel').exists():
            build['system'] = 'bazel'
            build['config_file'] = 'WORKSPACE'
            build['build_command'] = 'bazel build //...'
            build['test_command'] = 'bazel test //...'
            build['clean_command'] = 'bazel clean'

        # Meson
        elif (self.project_root / 'meson.build').exists():
            build['system'] = 'meson'
            build['config_file'] = 'meson.build'
            build['configure_command'] = 'meson setup build'
            build['build_command'] = 'meson compile -C build'
            build['test_command'] = 'meson test -C build'
            build['clean_command'] = 'rm -rf build'

        # Autotools
        elif (self.project_root / 'configure.ac').exists() or (self.project_root / 'configure.in').exists():
            build['system'] = 'autotools'
            build['config_file'] = 'configure.ac'
            build['configure_command'] = './configure'
            build['build_command'] = 'make'
            build['clean_command'] = 'make clean'
            build['test_command'] = 'make check'

        # SCons
        elif (self.project_root / 'SConstruct').exists():
            build['system'] = 'scons'
            build['config_file'] = 'SConstruct'
            build['build_command'] = 'scons'
            build['clean_command'] = 'scons -c'

        return build

    def _detect_compiler(self) -> Dict[str, Any]:
        """Detect compiler preferences"""
        compiler = {
            'preferred': None,
            'available': [],
        }

        # Check what's installed
        compilers_to_check = {
            'gcc': 'gcc --version',
            'g++': 'g++ --version',
            'clang': 'clang --version',
            'clang++': 'clang++ --version',
            'cl': 'cl',  # MSVC
            'icc': 'icc --version',  # Intel
        }

        for name, cmd in compilers_to_check.items():
            if self.check_tool_installed(name):
                compiler['available'].append(name)

        # Check CMake for compiler preference
        if (self.project_root / 'CMakeLists.txt').exists():
            cmake_content = self.read_file_lines(self.project_root / 'CMakeLists.txt')
            for line in cmake_content:
                if 'CMAKE_CXX_COMPILER' in line:
                    if 'clang' in line.lower():
                        compiler['preferred'] = 'clang++'
                    elif 'g++' in line or 'gcc' in line:
                        compiler['preferred'] = 'g++'
                    break

        # Check Makefile for compiler
        makefile = self._find_makefile()
        if makefile:
            make_content = self.read_file_lines(makefile)
            for line in make_content:
                if line.startswith('CXX'):
                    if 'clang' in line:
                        compiler['preferred'] = 'clang++'
                    elif 'g++' in line:
                        compiler['preferred'] = 'g++'
                    break
                elif line.startswith('CC') and not line.startswith('CXXFLAGS'):
                    if 'clang' in line:
                        compiler['preferred'] = 'clang'
                    elif 'gcc' in line:
                        compiler['preferred'] = 'gcc'

        # Default based on availability
        if not compiler['preferred'] and compiler['available']:
            if 'clang++' in compiler['available']:
                compiler['preferred'] = 'clang++'
            elif 'g++' in compiler['available']:
                compiler['preferred'] = 'g++'

        return compiler

    def _detect_standard(self) -> Optional[str]:
        """Detect C++ standard version"""
        # Check CMakeLists.txt
        if (self.project_root / 'CMakeLists.txt').exists():
            cmake_content = self.read_file_lines(self.project_root / 'CMakeLists.txt')
            for line in cmake_content:
                if 'CMAKE_CXX_STANDARD' in line:
                    match = re.search(r'CMAKE_CXX_STANDARD\s+(\d+)', line)
                    if match:
                        return f'c++{match.group(1)}'
                elif 'cxx_std_' in line.lower():
                    match = re.search(r'cxx_std_(\d+)', line.lower())
                    if match:
                        return f'c++{match.group(1)}'

        # Check Makefile
        makefile = self._find_makefile()
        if makefile:
            make_content = self.read_file_lines(makefile)
            for line in make_content:
                if 'std=' in line:
                    match = re.search(r'-std=c\+\+(\d+)', line)
                    if match:
                        return f'c++{match.group(1)}'
                    match = re.search(r'-std=gnu\+\+(\d+)', line)
                    if match:
                        return f'gnu++{match.group(1)}'

        return None

    def _detect_testing(self) -> Dict[str, Any]:
        """Detect testing framework"""
        testing = {
            'framework': None,
            'test_command': None,
        }

        # Check for common test frameworks
        test_frameworks = {
            'googletest': ['gtest', 'gmock'],
            'catch2': ['catch2', 'catch.hpp'],
            'boost.test': ['boost/test'],
            'cppunit': ['cppunit'],
            'doctest': ['doctest'],
        }

        # Search in CMakeLists.txt
        if (self.project_root / 'CMakeLists.txt').exists():
            cmake_content = ' '.join(self.read_file_lines(self.project_root / 'CMakeLists.txt', 200))
            cmake_lower = cmake_content.lower()

            for framework, markers in test_frameworks.items():
                for marker in markers:
                    if marker in cmake_lower:
                        testing['framework'] = framework
                        break

            # Check for CTest
            if 'enable_testing' in cmake_lower or 'ctest' in cmake_lower:
                testing['test_command'] = 'ctest'

        # Check for test directories
        test_dirs = ['test', 'tests', 'test_suite', 'spec']
        for dir_name in test_dirs:
            if (self.project_root / dir_name).is_dir():
                testing['test_dir'] = dir_name
                break

        return testing

    def _detect_dependencies(self) -> Dict[str, Any]:
        """Detect dependency management"""
        deps = {
            'manager': None,
            'config_file': None,
        }

        # Conan
        if (self.project_root / 'conanfile.txt').exists():
            deps['manager'] = 'conan'
            deps['config_file'] = 'conanfile.txt'
            deps['install_command'] = 'conan install .'
        elif (self.project_root / 'conanfile.py').exists():
            deps['manager'] = 'conan'
            deps['config_file'] = 'conanfile.py'
            deps['install_command'] = 'conan install .'

        # vcpkg
        elif (self.project_root / 'vcpkg.json').exists():
            deps['manager'] = 'vcpkg'
            deps['config_file'] = 'vcpkg.json'
            deps['install_command'] = 'vcpkg install'

        # CMake FetchContent (modern CMake)
        elif (self.project_root / 'CMakeLists.txt').exists():
            cmake_content = ' '.join(self.read_file_lines(self.project_root / 'CMakeLists.txt', 200))
            if 'FetchContent' in cmake_content:
                deps['manager'] = 'cmake-fetchcontent'
                deps['config_file'] = 'CMakeLists.txt'

        # Git submodules
        if (self.project_root / '.gitmodules').exists():
            if not deps['manager']:
                deps['manager'] = 'git-submodules'
            else:
                deps['also_uses'] = 'git-submodules'
            deps['submodule_init'] = 'git submodule update --init --recursive'

        return deps

    def _detect_project_type(self) -> str:
        """Detect project type"""
        # Check CMakeLists.txt for project type
        if (self.project_root / 'CMakeLists.txt').exists():
            cmake_content = self.read_file_lines(self.project_root / 'CMakeLists.txt', 100)
            has_library = False
            has_executable = False

            for line in cmake_content:
                if 'add_library' in line:
                    has_library = True
                if 'add_executable' in line:
                    has_executable = True

            if has_library and not has_executable:
                return 'library'
            elif has_executable and not has_library:
                return 'application'
            elif has_library and has_executable:
                return 'mixed'

        # Check for main.c/cpp
        if (self.find_files('**/main.c') or self.find_files('**/main.cpp') or
            self.find_files('**/main.cc')):
            return 'application'

        # Check for headers only
        h_files = (len(self.find_files('**/*.h')) +
                  len(self.find_files('**/*.hpp')))
        impl_files = (len(self.find_files('**/*.c')) +
                     len(self.find_files('**/*.cpp')) +
                     len(self.find_files('**/*.cc')))

        if h_files > 0 and impl_files == 0:
            return 'header-only'

        return 'unknown'

    def _find_makefile(self) -> Optional[Path]:
        """Find Makefile in project"""
        makefile_names = ['Makefile', 'makefile', 'GNUmakefile']
        for name in makefile_names:
            path = self.project_root / name
            if path.exists():
                return path
        return None

    def _parse_makefile_targets(self, makefile: Path) -> List[str]:
        """Extract targets from Makefile"""
        targets = []
        try:
            with open(makefile) as f:
                for line in f:
                    # Look for target definitions
                    if ':' in line and not line.startswith('\t') and not line.startswith(' '):
                        target = line.split(':')[0].strip()
                        if target and not target.startswith('.'):
                            targets.append(target)
        except:
            pass
        return targets

    def _check_cmake_language(self) -> Optional[str]:
        """Check CMakeLists.txt for language"""
        cmake_file = self.project_root / 'CMakeLists.txt'
        if cmake_file.exists():
            content = ' '.join(self.read_file_lines(cmake_file, 50))
            if 'LANGUAGES CXX' in content or 'LANGUAGES CXX C' in content:
                return 'c++'
            elif 'LANGUAGES C' in content:
                return 'c'
        return None