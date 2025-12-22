# Compiler and flags
CXX = g++
CXXFLAGS = -O2 -g
LDFLAGS = -lprofiler
PROFILER_LIB = /lib/x86_64-linux-gnu/libprofiler.so

# Tools
PPROF = /home/shihyu/go-workspace/bin/pprof

# Files
TARGET = app
SRC = main.cpp
PROF_CPU = tests/cpu.prof
PROF_REAL = tests/wall.prof
PDF_CPU = tests/cpu.pdf
PDF_REAL = tests/wall.pdf

.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help message
	@echo "Available targets:"
	@echo "  make build       - Build the project"
	@echo "  make run-cpu     - Run with standard CPU profiling (On-CPU only)"
	@echo "  make run-fgprof  - Run with Wall-clock profiling (On-CPU + Off-CPU)"
	@echo "  make report      - Generate PDF reports for comparison"
	@echo "  make clean       - Clean build artifacts"

.PHONY: build
build:  ## Build the project
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)

.PHONY: run-cpu
run-cpu: build  ## Run standard CPU profiling
	@echo "Running standard CPU profiling..."
	LD_PRELOAD=$(PROFILER_LIB) CPUPROFILE=$(PROF_CPU) ./$(TARGET)
	@echo "CPU profile saved to $(PROF_CPU)"

.PHONY: run-fgprof
run-fgprof: build  ## Run Wall-clock profiling (fgprof equivalent)
	@echo "Running Wall-clock profiling (CPUPROFILE_REALTIME=1)..."
	LD_PRELOAD=$(PROFILER_LIB) CPUPROFILE_REALTIME=1 CPUPROFILE_FREQUENCY=100 CPUPROFILE=$(PROF_REAL) ./$(TARGET)
	@echo "Wall-clock profile saved to $(PROF_REAL)"

.PHONY: report
report:  ## Generate PDF reports
	@echo "Generating CPU report..."
	$(PPROF) --pdf ./$(TARGET) $(PROF_CPU) > $(PDF_CPU)
	@echo "Generating Wall-clock report..."
	$(PPROF) --pdf ./$(TARGET) $(PROF_REAL) > $(PDF_REAL)
	@echo "Reports generated: $(PDF_CPU), $(PDF_REAL)"

.PHONY: clean
clean:  ## Clean environment
	rm -f $(TARGET)
	rm -rf tests/*.prof tests/*.pdf
